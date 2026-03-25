# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Development (via Makefile)
```bash
make setup       # First-time setup: venv + pip install + playwright install chromium
make dev         # Start everything: MongoDB (Docker) + FastAPI backend + React frontend
make db          # Start MongoDB only (Docker)
make backend     # Start FastAPI backend (uvicorn --reload on :8000)
make frontend    # Start React dev server (vite on :5173)
make lint        # Run ruff linter on backend
make test        # Run pytest
make clean       # Stop containers and remove volumes
```

### Manual startup
```bash
# Backend
cd backend && source venv/bin/activate
uvicorn main:app --reload --port 8000

# Frontend
cd frontend && npm run dev

# Single test
cd backend && pytest tests/path/to/test.py::test_name -v
```

### URLs
- Frontend: http://localhost:5173
- API + Swagger docs: http://localhost:8000/docs
- MongoDB: mongodb://localhost:27017

## Architecture

### Stack
- **Backend**: Python FastAPI + Motor (async MongoDB) + Playwright (browser automation) + APScheduler
- **Frontend**: React 18 + Vite + Tailwind CSS + React Router v6 + Recharts
- **Database**: MongoDB (collections: `jobs`, `applications`, `resumes`, `cover_letters`, `user_profile`, `scrape_logs`)
- **AI**: Claude via `kiro-cli` (subprocess wrapper in `backend/services/ai_service.py`); falls back to direct `ANTHROPIC_API_KEY` if set

### Backend module layout
```
backend/
├── main.py              # FastAPI app, lifespan (DB connect + scheduler start)
├── config.py            # Pydantic Settings loaded from .env, singleton via @lru_cache
├── database.py          # Motor async client, index creation, unique (portal, external_id)
├── models/              # Pydantic models: job.py, application.py, resume.py, user_profile.py
├── routers/             # API routes: jobs, applications, resumes, dashboard, settings
├── services/            # Business logic
│   ├── ai_service.py        # Kiro CLI subprocess wrapper
│   ├── job_matcher.py       # AI scoring: skills 35%, experience 25%, role 20%, location 10%, culture 10%
│   ├── resume_tailor.py     # Claude-powered resume rewriting + ATS optimization
│   ├── cover_letter_service.py
│   ├── pdf_generator.py     # Jinja2 + WeasyPrint → PDF
│   └── telegram_service.py  # Optional Telegram notifications
├── scrapers/            # Job scraping
│   ├── base_scraper.py      # Abstract: login(), search_jobs(), parse_job_detail(); manages Playwright lifecycle
│   ├── scraper_manager.py   # Orchestrates all portal scrapers sequentially, deduplicates, scores, notifies
│   └── {linkedin,naukri,wellfound,instahyre,indeed,glassdoor}_scraper.py
├── appliers/            # Auto-apply
│   ├── base_applier.py      # Extends BaseScraper; abstract apply_to_job()
│   ├── applier_manager.py   # Full pipeline: fetch → tailor resume → cover letter → PDFs → submit → record
│   └── {linkedin,naukri,wellfound,instahyre}_applier.py
└── schedulers/
    └── job_scheduler.py     # APScheduler: periodic scraping, auto-apply queue, daily Telegram summary
```

### Frontend module layout
```
frontend/src/
├── App.jsx             # React Router: /, /jobs, /applications, /resumes, /settings
├── api/client.js       # Axios instance; proxy /api → localhost:8000 (configured in vite.config.js)
├── pages/              # Dashboard, Jobs, Applications, ResumeManager, Settings
├── components/         # Layout, Sidebar, JobCard, StatusBadge, StatsCard, MatchScore, EmptyState
├── hooks/useApi.js     # Custom hook: loading/error/refetch state for API calls
└── utils/helpers.js    # Date formatting, portal icon mapping
```

### Key patterns

**Extending scrapers/appliers**: Subclass `BaseScraper` or `BaseApplier` and implement the abstract methods. Register the new class in `scraper_manager.py` / `applier_manager.py`.

**Auto-apply modes**: Controlled by `AUTO_APPLY_MODE` env var.
- `semi` — jobs queue for user review in the dashboard before applying
- `auto` — fully automatic; applies to any job above `MIN_MATCH_SCORE_TO_APPLY` (default: 70)

**AI calls go through `ai_service.py`** which shells out to `kiro-cli`. If kiro-cli isn't available, set `ANTHROPIC_API_KEY` for direct API access.

**Duplicate prevention**: MongoDB unique index on `(portal, external_id)`. Scrapers upsert on this key.

**Job status pipeline**: `new → reviewed → shortlisted → applied → interviewing → offered/rejected/accepted/expired/skipped`

**Application status pipeline**: `pending → submitted → reviewing → interview → offered → accepted/rejected/withdrawn`

## Environment setup

Copy `.env.example` to `.env`. Required fields:
- `MONGODB_URI` / `MONGODB_DB_NAME`
- Portal credentials for whichever portals you enable
- `TARGET_ROLES`, `TARGET_LOCATIONS`, `TARGET_SKILLS` — drive both scraping and AI scoring

`ANTHROPIC_API_KEY` is optional if `kiro-cli` is installed locally.
