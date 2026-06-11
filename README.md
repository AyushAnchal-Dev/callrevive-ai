# CallRevive AI — AI-Powered Missed Call Recovery Platform

CallRevive AI is an agentic, enterprise-grade SaaS application designed to help small businesses recover lost revenue from missed calls. The platform automatically intercepts missed calls, runs stateful voice/WhatsApp conversational callback loops via Twilio and Google Gemini, scores customer purchasing intent, forecasts revenue recovery, and routes alerts to business owners.

---

## 🚀 Key Features

*   **Stateful Dialogue Memory**: Multi-turn Voice AI dialogues with Redis caching and Gemini LLMs.
*   **Automatic Lead Qualification**: Extracts budget, services, and urgency to assign a lead score.
*   **Revenue Predictor & Score**: Flagship Gemini Pro pipeline to forecast revenue opportunities.
*   **Real-time Alerts**: WhatsApp, email, and SMS notifications for "Hot Leads" requiring owner action.
*   **Audio Recording Backup**: Automated download of call recordings, backed up to Backblaze B2.
*   **Premium React Dashboard**: Rich glassmorphic dashboard showcasing analytics, logs, funnel metrics, and calendars.

---

## 🛠️ Technology Stack

*   **Core API**: FastAPI, Python 3.12, Uvicorn, Gunicorn
*   **Frontend**: React, Vite, TypeScript, TailwindCSS v4, ShadCN UI
*   **Worker Queue**: Celery 5.6, RabbitMQ (CloudAMQP)
*   **Caching & Session Caching**: Redis (Upstash)
*   **Database**: PostgreSQL, SQLAlchemy 2.0, Alembic Migrations
*   **AI Models**: Google Gemini 2.5 Flash & Gemini 2.5 Pro (via `google-genai` SDK)
*   **Communication**: Twilio Voice, WhatsApp Business Sandbox, Multi-channel Dispatcher
*   **File Storage**: Backblaze B2 Object Storage (`b2sdk` integration)
*   **Containerization**: Docker, Docker Compose

---

## 📂 Project Directory Structure

```
callrevive-ai/
├── backend/                # FastAPI Application & Celery Worker
│   ├── app/                # Core API, Worker Tasks, AI, and Voice services
│   ├── alembic/            # Database version control and migration files
│   └── tests/              # Unit and Integration test suite (mocked & containerized)
├── frontend/               # React Dashboard & Tailwind v4 UI
├── infra/                  # Infrastructure configurations
│   ├── docker/             # Docker Compose & Nginx Proxy configurations
│   ├── k8s/                # Kubernetes deployments, services, ingress, and auto-scalers
│   └── argocd/             # GitOps Application definitions
└── docs/                   # Platform documentation
```

---

## 📖 Documentation Index

Please refer to the following documentation files in the `docs/` folder:

1.  [**Local Setup Guide**](docs/setup-guide.md): Instructions on getting API keys and booting up the stack locally with Docker Compose.
2.  [**Production Deployment Guide**](docs/deployment-guide.md): Steps to deploy the backend and worker containers to Render and Kubernetes (via ArgoCD GitOps).
3.  [**API Reference**](docs/api-reference.md): REST API specifications for registration, login, and Twilio webhook endpoints.
4.  [**Security Hardening Checklist**](docs/security-checklist.md): Step-by-step checklist to prepare the system for production.
5.  [**Testing Strategy**](docs/testing-strategy.md): Overview of unit testing, integration tests, database transaction isolation fixtures, and mocking strategies.
6.  [**Interactive Demo Script**](docs/demo-script.md): Instructions to simulate missed calls and voice dialogues using cURL.
