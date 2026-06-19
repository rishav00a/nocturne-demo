# nocturne-demo

[![django-nocturne](https://img.shields.io/badge/powered%20by-django--nocturne-blue)](https://pypi.org/project/django-nocturne/)
[![PyPI version](https://img.shields.io/pypi/v/django-nocturne)](https://pypi.org/project/django-nocturne/)

A minimal Django project demonstrating
[django-nocturne](https://github.com/rishav00a/django-nocturne)
installed directly from PyPI.

This repo is the live demo referenced in the django-nocturne
documentation and screenshots.

---

## What this demonstrates

- django-nocturne installed via pip (not from source)
- NocturneMiddleware auto-capturing all requests with zero code changes
- 2000 demo log entries across 6 realistic services
- 4 injected error spikes with full Python stacktraces
- AI anomaly diagnosis powered by Ollama (llama3.2, local and free)
- Live dashboard at /nocturne/dashboard/
- Django Admin integration at /admin/nocturne/dashboard/
- All 12 REST API endpoints working

---

## Services in the demo

| Service | Description |
|---------|-------------|
| auth-service | User authentication and JWT tokens |
| payment-service | Payment processing and billing |
| api-gateway | Upstream request routing |
| notification-service | Email and push notifications |
| user-service | User profile management |
| inventory-service | Product inventory tracking |

---

## Quick Start

```bash
git clone https://github.com/rishav00a/nocturne-demo
cd nocturne-demo
python -m venv venv
source venv/bin/activate
pip install django-nocturne[ollama]
python manage.py migrate
python manage.py createsuperuser
python seed.py
python manage.py snapshot_health
python manage.py runserver 8080
```

Visit:
- Dashboard: http://localhost:8080/nocturne/dashboard/
- Admin: http://localhost:8080/admin/
- API: http://localhost:8080/nocturne/api/health/

---

## Requirements

- Python 3.10+
- Ollama running locally
- llama3.2 model pulled

```bash
# Install and start Ollama
brew install ollama
ollama serve
ollama pull llama3.2
```

---

## Project Structure

```
nocturne-demo/
├── demo/
│   ├── settings.py        # NOCTURNE config lives here
│   ├── urls.py            # nocturne.urls mounted at /nocturne/
│   └── wsgi.py
├── seed.py                # Seeds 2000 log entries + 4 error spikes
├── manage.py
└── README.md
```

---

## NOCTURNE Settings

```python
NOCTURNE = {
    "AI_BACKEND": "ollama",
    "OLLAMA_BASE_URL": "http://localhost:11434",
    "OLLAMA_MODEL": "llama3.2",
    "ANOMALY_THRESHOLD": 2.0,
    "SERVICE_NAME": "demo-app",
    "AI_DIAGNOSIS_ENABLED": True,
    "LOGIN_URL": "/admin/login/",
}
```

---

## License

MIT
