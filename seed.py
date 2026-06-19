"""
Seed script — 2000 realistic LogEntry records with 4 error spikes within
the 30-minute detection window, then runs detection and health snapshots.

Usage:  python seed.py  (from inside the nocturne-demo directory)
"""

import os
import sys
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "demo.settings")
django.setup()

import random
import textwrap
from datetime import timedelta

from django.utils import timezone
from django.db import connection

from nocturne.models import LogEntry, AnomalyEvent, HealthSnapshot, WebhookConfig, WebhookEvent
from nocturne.detection import run_detection, take_health_snapshot

# ── constants ─────────────────────────────────────────────────────────────────

SERVICES = [
    "auth-service",
    "payment-service",
    "api-gateway",
    "notification-service",
    "user-service",
    "inventory-service",
]

PATHS = {
    "auth-service":         ["/api/auth/login/", "/api/auth/logout/", "/api/auth/refresh/", "/api/auth/verify/"],
    "payment-service":      ["/api/payments/charge/", "/api/payments/refund/", "/api/payments/status/", "/api/payments/methods/"],
    "api-gateway":          ["/api/v1/proxy/", "/api/v1/route/", "/api/v1/health/", "/api/v1/metrics/"],
    "notification-service": ["/api/notifications/send/", "/api/notifications/list/", "/api/notifications/read/"],
    "user-service":         ["/api/users/", "/api/users/profile/", "/api/users/settings/", "/api/users/search/"],
    "inventory-service":    ["/api/inventory/items/", "/api/inventory/stock/", "/api/inventory/reserve/"],
}

SOURCE_IPS = [f"10.{random.randint(0,3)}.{random.randint(0,255)}.{random.randint(1,254)}" for _ in range(60)]

RANDOM_ERRORS = [
    {
        "exception_type": "ValueError",
        "stacktrace": (
            "Traceback (most recent call last):\n"
            '  File "/app/api/views.py", line 88, in handle_request\n'
            "    validated = self.validate_payload(request.data)\n"
            '  File "/app/api/validators.py", line 23, in validate_field\n'
            "    return int(value)\n"
            "ValueError: Invalid input data: expected int got str"
        ),
    },
    {
        "exception_type": "TimeoutError",
        "stacktrace": (
            "Traceback (most recent call last):\n"
            '  File "/app/api/views.py", line 56, in get\n'
            "    data = self.cache.get_or_compute(key, compute_fn)\n"
            '  File "/app/core/cache.py", line 89, in get_cached\n'
            "    result = redis_client.get(key, timeout=3.0)\n"
            "TimeoutError: Redis cache timeout after 3000ms"
        ),
    },
]

SPIKE_STACKTRACES = {
    "DatabaseConnectionError": (
        "Traceback (most recent call last):\n"
        '  File "/app/payment_service/views.py", line 142, in process_charge\n'
        "    conn = db_pool.acquire(timeout=5.0)\n"
        '  File "/app/lib/db/pool.py", line 89, in acquire\n'
        "    return self._connect(host=self.primary_host, port=5432)\n"
        '  File "/app/lib/db/pool.py", line 203, in _connect\n'
        "    raise DatabaseConnectionError(f\"Cannot connect to {host}:{port}\")\n"
        "payment_service.exceptions.DatabaseConnectionError: Cannot connect to postgres-primary:5432 — Connection timed out"
    ),
    "UpstreamTimeoutError": (
        "Traceback (most recent call last):\n"
        '  File "/app/gateway/proxy.py", line 78, in forward_request\n'
        "    resp = httpx_client.post(upstream_url, json=payload, timeout=self.timeout)\n"
        '  File "/usr/local/lib/python3.11/site-packages/httpx/_client.py", line 783, in _send\n'
        "    raise ConnectTimeout(str(exc), request=request)\n"
        "httpx.ConnectTimeout: [Errno 110] Connection timed out\n"
        '  File "/app/gateway/middleware.py", line 44, in dispatch\n'
        "    raise UpstreamTimeoutError(f\"Upstream timed out after {self.timeout}s\")\n"
        "gateway.exceptions.UpstreamTimeoutError: Upstream 'http://auth-service:8001/' timed out after 30s"
    ),
    "TokenValidationError": (
        "Traceback (most recent call last):\n"
        '  File "/app/auth_service/views.py", line 55, in verify_token\n'
        "    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[\"HS256\"])\n"
        '  File "/usr/local/lib/python3.11/site-packages/jose/jwt.py", line 149, in decode\n'
        "    payload = jws.verify(token, key, algorithms)\n"
        '  File "/usr/local/lib/python3.11/site-packages/jose/jws.py", line 197, in verify\n'
        '    raise JWTError("Signature has expired.")\n'
        "jose.exceptions.JWTError: Signature has expired.\n"
        '  File "/app/auth_service/middleware.py", line 92, in authenticate\n'
        "    raise TokenValidationError(f\"JWT validation failed: {exc}\")\n"
        "auth_service.exceptions.TokenValidationError: JWT validation failed: Signature has expired."
    ),
    "CacheConnectionError": (
        "Traceback (most recent call last):\n"
        '  File "/app/inventory_service/cache.py", line 33, in get_stock\n'
        "    return redis_client.hgetall(f\"stock:{item_id}\")\n"
        '  File "/usr/local/lib/python3.11/site-packages/redis/client.py", line 1226, in execute_command\n'
        "    connection = self.connection_pool.get_connection(command_name)\n"
        '  File "/usr/local/lib/python3.11/site-packages/redis/connection.py", line 563, in connect\n'
        "    raise ConnectionError(self._error_message(e))\n"
        "redis.exceptions.ConnectionError: Error 111 connecting to redis-cache:6379. Connection refused.\n"
        '  File "/app/inventory_service/views.py", line 78, in reserve_stock\n'
        "    raise CacheConnectionError(\"Redis unavailable — cannot verify stock levels\")\n"
        "inventory_service.exceptions.CacheConnectionError: Redis unavailable — cannot verify stock levels"
    ),
}


def rand_level():
    r = random.random()
    if r < 0.60:  return "INFO"
    if r < 0.80:  return "WARNING"
    if r < 0.95:  return "ERROR"
    return "CRITICAL"


def rand_status(level):
    if level == "CRITICAL": return random.choice([500, 503, 500, 503])
    if level == "ERROR":    return random.choice([500, 503, 400, 404])
    if level == "WARNING":  return random.choice([400, 401, 404, 200])
    return random.choice([200, 200, 200, 201])


def rand_rt(level):
    if level in ("ERROR", "CRITICAL"): return random.randint(800, 3000)
    if level == "WARNING":             return random.randint(200, 900)
    return random.randint(10, 350)


def hour_weight(hour):
    if 9 <= hour <= 17:  return 3.0
    if 18 <= hour <= 22: return 1.5
    if 0 <= hour <= 5:   return 0.4
    return 1.0


# ── clear + seed ──────────────────────────────────────────────────────────────

print("Clearing existing nocturne data…")
WebhookEvent.objects.all().delete()
HealthSnapshot.objects.all().delete()
AnomalyEvent.objects.all().delete()
LogEntry.objects.all().delete()

now     = timezone.now()
entries = []

# ── 2000 baseline entries across last 24 hours ────────────────────────────────

print("Generating baseline traffic (2000 entries across last 24 h)…")
generated = 0
while generated < 2000:
    svc     = random.choice(SERVICES)
    offset  = timedelta(seconds=random.uniform(0, 86400))
    ts      = now - offset
    weight  = hour_weight(ts.hour)
    if random.random() > weight / 3.0:
        continue  # thin out low-volume hours
    level   = rand_level()
    path    = random.choice(PATHS[svc])
    err     = random.choice(RANDOM_ERRORS) if level in ("ERROR", "CRITICAL") else {}
    entries.append(LogEntry(
        service_name      = svc,
        timestamp         = ts,
        level             = level,
        message           = err.get("stacktrace", "").splitlines()[-1] if err else f"HTTP {rand_status(level)} {path}",
        request_path      = path,
        status_code       = rand_status(level),
        response_time_ms  = rand_rt(level),
        source_ip         = random.choice(SOURCE_IPS),
        exception_type    = err.get("exception_type"),
        stacktrace        = err.get("stacktrace"),
    ))
    generated += 1

print(f"  Generated {len(entries)} baseline entries")

# ── 4 error spikes — all WITHIN the 30-minute detection window ───────────────
#    Detection scans the last 30 minutes, split into 6 × 5-minute buckets.
#    Each spike floods 1–2 buckets to ensure Z-score >> threshold.

SPIKES = [
    dict(service="payment-service",     ago=timedelta(minutes=27), count=45, dur=180,
         level="CRITICAL", exc="DatabaseConnectionError", path="/api/payments/charge/",  code=503),
    dict(service="api-gateway",         ago=timedelta(minutes=18), count=50, dur=120,
         level="ERROR",    exc="UpstreamTimeoutError",    path="/api/v1/proxy/",         code=504),
    dict(service="auth-service",        ago=timedelta(minutes=10), count=60, dur=90,
         level="CRITICAL", exc="TokenValidationError",    path="/api/auth/verify/",      code=401),
    dict(service="inventory-service",   ago=timedelta(minutes=4),  count=35, dur=120,
         level="ERROR",    exc="CacheConnectionError",    path="/api/inventory/stock/",  code=500),
]

for sp in SPIKES:
    base = now - sp["ago"]
    exc  = sp["exc"]
    print(f"  Injecting spike: {sp['service']} @ {sp['ago']} ago ({sp['count']} entries)…")
    for _ in range(sp["count"]):
        ts = base + timedelta(seconds=random.uniform(0, sp["dur"]))
        entries.append(LogEntry(
            service_name     = sp["service"],
            timestamp        = ts,
            level            = sp["level"],
            message          = f"{exc}: {sp['path']} — {sp['code']}",
            request_path     = sp["path"],
            status_code      = sp["code"],
            response_time_ms = random.randint(2000, 3000),
            source_ip        = random.choice(SOURCE_IPS),
            exception_type   = exc,
            stacktrace       = SPIKE_STACKTRACES[exc],
        ))

# ── bulk insert + timestamp fix ───────────────────────────────────────────────

# Capture BEFORE bulk_create — auto_now_add overwrites .timestamp on save
intended_timestamps = [e.timestamp for e in entries]

print(f"\nBulk inserting {len(entries)} entries…")
created = LogEntry.objects.bulk_create(entries, batch_size=500)

print("Fixing timestamps via raw SQL (auto_now_add bypass)…")
table = LogEntry._meta.db_table
with connection.cursor() as cur:
    cur.executemany(
        f"UPDATE {table} SET timestamp = %s WHERE id = %s",
        [(ts.isoformat(sep=" "), obj.id) for ts, obj in zip(intended_timestamps, created)],
    )
print(f"  Total LogEntries: {LogEntry.objects.count()}")

# ── detection ─────────────────────────────────────────────────────────────────

print("\nRunning anomaly detection…")
anomalies = run_detection()
print(f"  AnomalyEvents created: {len(anomalies)}")

# ── health snapshots (two passes for trend data) ──────────────────────────────

print("Taking health snapshots (2 passes for trend arrows)…")
take_health_snapshot()
take_health_snapshot()

# Seed historical snapshots per service for Health Trends panel
snap_entries = []
for svc in SERVICES:
    for j in range(13):
        snap_time = now - timedelta(hours=2) + timedelta(minutes=j * 10)
        if svc == "auth-service":
            score = max(10.0, 85.0 - j * 5)
        elif svc == "payment-service":
            score = max(15.0, 90.0 - j * 4)
        elif svc == "inventory-service":
            score = max(20.0, 80.0 - j * 3)
        else:
            score = random.uniform(65, 95)
        snap_entries.append(HealthSnapshot(
            service_name  = svc,
            health_score  = round(score, 1),
            error_rate    = round(max(0, (100 - score) / 5), 2),
            request_count = random.randint(50, 300),
            anomaly_count = 1 if score < 40 else 0,
            recorded_at   = snap_time,
        ))

created_snaps = HealthSnapshot.objects.bulk_create(snap_entries)
snap_table    = HealthSnapshot._meta.db_table
snap_times    = [s.recorded_at for s in snap_entries]
with connection.cursor() as cur:
    cur.executemany(
        f"UPDATE {snap_table} SET recorded_at = %s WHERE id = %s",
        [(ts.isoformat(sep=" "), obj.id) for ts, obj in zip(snap_times, created_snaps)],
    )
print(f"  HealthSnapshots: {HealthSnapshot.objects.count()}")

# ── webhook config (simulated receiver) ───────────────────────────────────────

wh_cfg, _ = WebhookConfig.objects.get_or_create(
    name="Simulated Receiver",
    defaults={
        "url":          "http://127.0.0.1:8080/nocturne/api/webhook/receive/",
        "is_active":    True,
        "secret_token": "demo-secret-token",
    },
)

# Seed demo WebhookEvents for the anomalies found
anomaly_list = list(AnomalyEvent.objects.all())
wh_events = []
for i, a in enumerate(anomaly_list[:4]):
    success = (i % 3 != 1)
    wh_events.append(WebhookEvent(
        anomaly         = a,
        webhook_config  = wh_cfg,
        payload         = {"event": "anomaly.detected", "anomaly": {"id": a.pk, "service": a.service_name, "severity": a.severity}},
        response_status = 200 if success else None,
        response_body   = '{"status":"received"}' if success else "",
        success         = success,
        error_message   = "" if success else "Connection refused: 127.0.0.1:9999",
    ))

if wh_events:
    created_wh = WebhookEvent.objects.bulk_create(wh_events)
    wh_times   = [now - timedelta(minutes=30 - i * 7) for i in range(len(wh_events))]
    wh_table   = WebhookEvent._meta.db_table
    with connection.cursor() as cur:
        cur.executemany(
            f"UPDATE {wh_table} SET triggered_at = %s WHERE id = %s",
            [(ts.isoformat(sep=" "), obj.id) for ts, obj in zip(wh_times, created_wh)],
        )
    print(f"  WebhookEvents: {WebhookEvent.objects.count()}")

print(f"\nFinal counts:")
print(f"  LogEntries    : {LogEntry.objects.count()}")
print(f"  AnomalyEvents : {AnomalyEvent.objects.count()}")
print(f"  HealthSnapshots: {HealthSnapshot.objects.count()}")
print(f"  WebhookEvents : {WebhookEvent.objects.count()}")
print("\nSeed complete.")
