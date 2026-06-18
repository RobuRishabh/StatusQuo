# StatusQuo

Automated weekly status report agent that aggregates your work contributions from GitHub, GitLab, Jira, and Confluence into a unified report.

## What It Does

- **Auto-collects** PRs raised/reviewed (GitHub Cloud, Enterprise, GitLab Cloud, Self-managed)
- **Tracks Jira** tickets, reads the "Git Pull Request" field and comments for proof
- **Scans Confluence** for new/updated documentation pages
- **Deduplicates** proof across sources (deterministic URL matching + LLM fuzzy matching)
- **AI-summarizes** every contribution into 1-line descriptions using GPT-4o-mini
- **Manual entries** for blogs, talks, awards, org memberships (with photo uploads)
- **Weekly reports** published every Friday at 6 PM EST
- **Delivery channels**: UI (active), Email and Slack (stubbed for Phase 2)

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12 + FastAPI |
| Frontend | Next.js 14 + Tailwind CSS |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy 2.0 (async) |
| LLM | OpenAI GPT-4o-mini via LiteLLM |
| Scheduler | APScheduler |
| Auth | GitHub OAuth 2.0 + password/PAT |

## Quick Start

### Prerequisites

- Docker and Docker Compose
- (Optional) GitHub OAuth App for OAuth login
- (Optional) API tokens for GitHub, GitLab, Jira, Confluence, OpenAI

### 1. Configure environment

```bash
cp .env.example .env
# Edit .env with your API tokens
```

### 2. Start everything

```bash
docker-compose up --build
```

This starts:
- **PostgreSQL** on port 5432
- **Backend API** on http://localhost:8000 (Swagger docs at /docs)
- **Frontend** on http://localhost:3000

### 3. Create an account

Visit http://localhost:3000, register with a username/password, then go to Settings to link your GitHub/GitLab/Jira/Confluence accounts.

### 4. Collect data

From your profile page, click "Sync Data" to trigger collection, then "Generate Report" to compile your weekly status.

## Running Without Docker

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Make sure PostgreSQL is running and .env is configured
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Project Structure

```
StatusQuo/
  backend/
    app/
      main.py                     # FastAPI entrypoint
      config.py                   # Environment-based settings
      models/                     # SQLAlchemy models
      api/routes/                 # REST API endpoints
      collectors/                 # GitHub, GitLab, Jira, Confluence collectors
      services/                   # Dedup, summarizer, report, scheduler
      delivery/                   # UI, Email (stub), Slack (stub)
      db/                         # Database session
  frontend/
    src/
      app/                        # Next.js pages
      components/                 # React components
      lib/                        # API client, auth context
  docker-compose.yml
  .env.example
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/register | Register with password |
| POST | /api/auth/login | Login with password |
| GET | /api/auth/github/login | Start GitHub OAuth |
| GET | /api/users/search?q= | Search users |
| GET | /api/users/me | Current user profile |
| GET | /api/contributions/me | My contributions |
| POST | /api/manual-entries/ | Add manual entry |
| GET | /api/reports/me | My reports |
| POST | /api/reports/trigger-collection | Trigger data sync |
| POST | /api/reports/trigger-report | Generate report |

## Scheduled Jobs

- **Nightly (2 AM EST)**: Collects fresh data from all sources for all users
- **Friday (6 PM EST)**: Compiles weekly reports and delivers via active channels
