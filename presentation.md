# django-nocturne — Architecture & Project Overview

**Candidate:** Rishav  
**Date:** June 19, 2026  
**Project:** Intelligent Observability & Event Watchdog  
**Package:** django-nocturne  

---

## 🏷️ Tagle.ai Profile

**Tag: The Architect** *(with a Navigator edge · Developing)*

> "You master what others skim — depth is your edge"

| Dimension | Score |
|-----------|-------|
| Growth Mindset | 72 |
| Autonomy | 75 |
| Competence | 76 |
| Relatedness | 58 |
| Innovation Readiness | 52 |

**AI Fluency Level:** Confident Operator — Developing mindset · High skills  
**Assessment completed:** June 18, 2026  
**Daily AI Tools:** ChatGPT, Claude, Gemini, Microsoft Copilot, GitHub Copilot, Midjourney, Notion AI  

**Profile Summary:**  
Operates with high technical self-efficacy, treating intelligence as a tool to be sharpened. Comfortable navigating macro-level AI shifts, treating complex systems as puzzles to be solved. High internal locus of control enables quick pivoting when facing technical hurdles.

**Key Strengths identified by Tagle:**
- Technical Self-Reliance: Daily AI tool usage without waiting for institutional adoption
- Analytical Synthesis: Ability to connect disparate domains and spot patterns others miss
- Resilience in Problem-Solving: Views failure as data, enabling rapid iteration without ego

**Relevance to this project:**  
The Architect tag directly shaped this submission — rather than building a standalone script, I designed a reusable, pip-installable Django package with a 3-layer AI pipeline, full documentation, CI/CD, and PyPI distribution. Depth over breadth.

---

## 📋 Submission Checklist

| Requirement | Status | Link / Notes |
|-------------|--------|--------------|
| Tagle.ai Tag output | ✅ Complete | See above — The Architect |
| Public GitHub Repository | ✅ Live | https://github.com/rishav00a/django-nocturne |
| prompts.md audit log | ✅ Complete | https://github.com/rishav00a/nocturne-demo/tree/main/claude_prompts |
| Architecture Presentation | ✅ Complete | https://github.com/rishav00a/nocturne-demo/blob/main/presentation.md |
| Cloud resources decommissioned | ✅ Confirmed | SQLite + Ollama (local only, zero cloud spend) |

---

## 🎁 Bonus Deliverables

| Deliverable | Link |
|-------------|------|
| 📦 PyPI Package (pip installable) | https://pypi.org/project/django-nocturne/ |
| 📚 ReadTheDocs Documentation | https://django-nocturne.readthedocs.io |
| 🧪 Demo Implementation Project | https://github.com/rishav00a/nocturne-demo |
| 🎯 Architecture Presentation Deck | https://github.com/rishav00a/nocturne-demo/blob/main/presentation.md |
| 🔄 GitHub Actions CI/CD | https://github.com/rishav00a/django-nocturne/actions |

---

## 🧪 Demo Implementation Project

To demonstrate real-world usage of the package, I created a separate implementation repository:

**Demo Repository:** https://github.com/rishav00a/nocturne-demo  

This project consumes the published `django-nocturne` package exactly as an end user would. It serves as a complete working example of:

- Installing the package from PyPI  
- Configuring observability in a Django application  
- Generating and ingesting logs  
- Running anomaly detection workflows  
- Triggering webhook alerts  
- Visualizing health metrics through the dashboard  

The architecture presentation for the system is included in this demo repository:

https://github.com/rishav00a/nocturne-demo/blob/main/presentation.md  

---

## 🎯 Project Selection & Rationale

**Chosen:** Project 3 — Intelligent Observability & Event Watchdog

**Why this project:**
- Most aligned with the Agentic Orchestration theme emphasized in the brief
- No real cloud account needed — synthetic logs avoid accidental cloud costs entirely
- Webhook + dashboard combination creates the most visually impressive and verifiable demo
- SRE/observability is a high-value skill in enterprise platform engineering
- Allowed me to go deeper than a script — built a real open source package

---

## 🏗️ What Was Built

Rather than a standalone app, I built **django-nocturne** — a reusable, pip-installable Django observability package that any Django project can attach to with 3 lines of configuration.

```bash
pip install django-nocturne[ollama]
```

```python
# settings.py
INSTALLED_APPS = [..., 'nocturne']
MIDDLEWARE = [..., 'nocturne.middleware.NocturneMiddleware']
NOCTURNE = {'AI_BACKEND': 'ollama', 'OLLAMA_MODEL': 'llama3.2'}
```

```bash
python manage.py migrate
# Full observability immediately at /nocturne/dashboard/
```

---

## 🤖 AI Logic — 3-Layer Detection Pipeline

The assessment required "AI logic" for anomaly detection. I implemented a layered pipeline:

### Layer 1 — Statistical Engine (Z-score)
- Counts errors per 5-minute bucket per service
- Computes Z-score across a 30-minute rolling window
- Flags when error rate deviates >2 standard deviations
- Industry-standard approach used by Datadog, New Relic, Prometheus

### Layer 2 — Multi-Signal Health Scoring
- Combines 3 signals into a 0-100 health score:
  - Error rate: 50% weight
  - Response time vs baseline: 30% weight
  - Request volume drop: 20% weight
- Tracks trend direction: improving ↑ / stable → / degrading ↓
- Stored as HealthSnapshot for historical comparison

### Layer 3 — LLM Root Cause Diagnosis
- When anomaly confirmed, sends last 50 log entries + stacktrace to an LLM via LangChain
- Supports 4 configurable backends:
  - Ollama (local, completely free)
  - OpenAI / ChatGPT
  - Anthropic Claude
  - Google Gemini
- Returns 3-sentence structured diagnosis:
  1. Root cause
  2. Immediate fix
  3. Prevention measure
- Result cached on AnomalyEvent — LLM called only once per anomaly

---

## 🔔 Webhook Alert System

When thresholds are breached the system:
1. Creates AnomalyEvent with severity + Z-score
2. POSTs structured payload to all active WebhookConfigs
3. Creates WebhookEvent tracking delivery success/failure/timeout
4. Dashboard shows live webhook activity feed
5. `/api/webhook/receive/` acts as the simulated receiver

Webhook payload:

```json
{
  "event": "anomaly.detected",
  "timestamp": "2026-06-19T03:22:27Z",
  "anomaly": {
    "service": "auth-service",
    "severity": "CRITICAL",
    "z_score": 4.7,
    "error_count": 50,
    "ai_diagnosis": "JWT validation failures suggest..."
  },
  "health": {
    "score_before": 85.0,
    "score_after": 20.0,
    "trend": "degrading"
  },
  "action_required": true
}
```

---

## 📦 Package Architecture

```
django-nocturne/
├── nocturne/                    # Reusable pip-installable app
│   ├── middleware.py            # Auto request/response capture
│   ├── models.py                # LogEntry, AnomalyEvent,
│   │                            # WebhookConfig, WebhookEvent,
│   │                            # HealthSnapshot
│   ├── detection.py             # 3-layer AI pipeline
│   ├── ai_diagnosis.py          # LangChain multi-backend LLM
│   ├── views.py                 # 12 DRF API endpoints
│   ├── admin.py                 # Custom Django Admin dashboard
│   ├── permissions.py           # Superuser + viewer tiers
│   └── management/commands/     # 4 management commands
│       ├── nocturne_config.py
│       ├── test_ai_diagnosis.py
│       ├── create_nocturne_user.py
│       └── snapshot_health.py
├── example_project/             # Demo Django project
├── tests/                       # pytest test suite
├── docs/                        # Sphinx + ReadTheDocs
└── .github/workflows/           # CI (test) + CD (publish)
    ├── ci.yml                   # Tests on Python 3.9–3.12
    └── publish.yml              # Auto-publish on GitHub Release
```

---

## 🛠️ Tech Stack

| Component | Technology | Why |
|-----------|------------|-----|
| Framework | Django 4.2+ / 5.1+ | Requirement |
| API | Django REST Framework | API-first requirement |
| Database | SQLite | Free tier requirement |
| AI/LLM | LangChain | Unified multi-backend interface |
| Anomaly Detection | numpy Z-score | Statistical AI logic |
| Dashboard | Chart.js (dark theme) | Visualization requirement |
| Packaging | pyproject.toml + setuptools | pip installable |
| CI/CD | GitHub Actions | Auto-test + auto-publish |
| Docs | Sphinx + ReadTheDocs | Professional documentation |
| Distribution | PyPI | Public package registry |

---

## 📊 API Endpoints (12 total)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/nocturne/api/health/` | System health summary |
| GET | `/nocturne/api/logs/` | Paginated log list |
| POST | `/nocturne/api/logs/ingest/` | Manual log ingestion |
| GET | `/nocturne/api/logs/{id}/` | Single log with stacktrace |
| POST | `/nocturne/api/logs/{id}/analyse/` | Per-log AI analysis |
| POST | `/nocturne/api/detect/` | Run detection scan |
| GET | `/nocturne/api/anomalies/` | List anomaly events |
| PATCH | `/nocturne/api/anomalies/{id}/` | Mark as resolved |
| GET | `/nocturne/api/webhooks/` | List webhook configs |
| POST | `/nocturne/api/webhooks/` | Create webhook |
| GET | `/nocturne/api/webhooks/events/` | Delivery history |
| POST | `/nocturne/api/webhooks/test/` | Send test webhook |

---

## 📸 Screenshots

### Dashboard Overview
![Dashboard Overview](https://raw.githubusercontent.com/rishav00a/django-nocturne/main/docs/screenshots/dashboard_overview.png)

### Error Rate & Service Health Charts
![Charts](https://raw.githubusercontent.com/rishav00a/django-nocturne/main/docs/screenshots/dashboard_charts.png)

### Anomaly Detection Table
![Anomaly Table](https://raw.githubusercontent.com/rishav00a/django-nocturne/main/docs/screenshots/dashboard_anomaly_table.png)

### Anomaly Modal with Z-Score Meter & AI Diagnosis
![Anomaly Modal](https://raw.githubusercontent.com/rishav00a/django-nocturne/main/docs/screenshots/anomaly_modal.png)

### Log Explorer
![Log Explorer](https://raw.githubusercontent.com/rishav00a/django-nocturne/main/docs/screenshots/log_explorer.png)

### Stacktrace Viewer with AI Analysis
![Stacktrace](https://raw.githubusercontent.com/rishav00a/django-nocturne/main/docs/screenshots/log_stacktrace.png)

### AI Root Cause Analysis
![AI Analysis](https://raw.githubusercontent.com/rishav00a/django-nocturne/main/docs/screenshots/log_ai_analysis.png)

### Health Trends
![Health Trends](https://raw.githubusercontent.com/rishav00a/django-nocturne/main/docs/screenshots/health_trends.png)

### Django Admin Integration
![Admin Dashboard](https://raw.githubusercontent.com/rishav00a/django-nocturne/main/docs/screenshots/admin_dashboard.png)

---

## 🔄 Vibe Coding Workflow

**Strictly followed the no-manual-edits rule throughout:**

- ✅ All code generated by Claude (Anthropic)
- ✅ All bug fixes described to AI in natural language
- ✅ prompts.md maintained with full chronological audit log in the demo repo
- ✅ Same AI tool (Claude) used end-to-end for consistency
- ✅ Human-in-the-Loop: I made all architectural decisions, AI executed all implementation

**My role as Architect (consistent with Tagle Tag):**
- Designed the 3-layer detection pipeline architecture
- Decided to build a reusable package vs standalone app
- Chose Django + DRF + LangChain as the tech stack
- Directed each build phase via precise, structured prompts
- Debugged issues by describing symptoms to the AI
- Made all product decisions: features, UX, naming, packaging

**AI's role as Engineer:**
- Generated all Python, HTML, CSS, JavaScript code
- Fixed bugs when described in natural language
- Built the dashboard UI and admin integration
- Wrote tests, documentation, and CI/CD workflows
- Suggested implementation patterns when asked

---

## 💡 Architect Tag — Reflection

The Tagle assessment identified me as an Architect who goes deep while others scan headlines. This submission directly reflects that:

| Instead of... | I built... |
|---------------|------------|
| A standalone script | A pip-installable reusable package |
| One LLM backend | A configurable 4-backend system via LangChain |
| A basic bar chart | A production-grade APM dashboard |
| A GitHub repo | PyPI + ReadTheDocs + CI/CD + Demo repo |
| Manual deployment | GitHub Actions auto-publish pipeline |

The growth opportunity Tagle identified — moving from solo operator to team-based innovator — is directly addressed by making this open source. Anyone can now `pip install django-nocturne` and benefit from this work, and contributions are welcome via GitHub.

---

## 🔗 All Submission Links

| Resource | URL |
|----------|-----|
| 📦 PyPI Package | https://pypi.org/project/django-nocturne/ |
| 🐙 GitHub Repository | https://github.com/rishav00a/django-nocturne |
| 🧪 Demo Project | https://github.com/rishav00a/nocturne-demo |
| 📚 Documentation | https://django-nocturne.readthedocs.io |
| 🔄 CI/CD Actions | https://github.com/rishav00a/django-nocturne/actions |
| 📝 Prompts Audit Log | https://github.com/rishav00a/nocturne-demo/tree/main/claude_prompts |
| 🎯 Architecture Deck | https://github.com/rishav00a/nocturne-demo/blob/main/presentation.md |

---

*Built with Claude (Anthropic) as the AI engineering agent.*  
*Architected, directed, and submitted by Rishav — June 19, 2026.*

> "You master what others skim — depth is your edge."
