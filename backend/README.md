# JobPilot Backend

Python FastAPI backend — API server, job scraping, AI integration, and data management.

## Quick Start

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

API docs at `http://localhost:8000/docs`

## Structure

```
backend/
├── main.py              # FastAPI app, lifespan, CORS, router registration
├── config.py            # Pydantic settings from .env
├── database.py          # MongoDB async connection (Motor)
│
├── routers/             # API endpoints
│   ├── auth.py          # Register, login, JWT, field-level validation
│   ├── jobs.py          # CRUD, scrape, score, export CSV, manual add, fetch URL
│   ├── applications.py  # Application tracking, status updates
│   ├── resumes.py       # LaTeX editor, compile to PDF, AI tailoring
│   ├── dashboard.py     # Stats, timeline, portals, salary insights
│   └── settings.py      # Profile, preferences, rules, scheduler, portals
│
├── services/            # Business logic
│   ├── ai_service.py    # Kiro CLI wrapper (no API key needed)
│   ├── resume_tailor.py # AI resume tailoring with rules + profile
│   ├── job_matcher.py   # Quick score (heuristic) + AI score
│   ├── job_parser.py    # URL parser — extracts job details from any URL
│   ├── user_prefs.py    # Per-user preferences from MongoDB
│   ├── auth_service.py  # JWT + bcrypt
│   ├── cover_letter_service.py
│   └── telegram_service.py
│
├── scrapers/
│   └── scraper_manager.py  # python-jobspy wrapper, keyword expansion
│
├── schedulers/
│   └── job_scheduler.py    # APScheduler for periodic scraping
│
├── models/              # Pydantic schemas
│   ├── job.py           # Job, JobCreate, JobUpdate, JobStatus
│   ├── application.py   # Application model
│   ├── resume.py        # Resume, CoverLetter
│   ├── user.py          # UserCreate, UserLogin
│   └── user_profile.py  # User profile/preferences
│
├── tests/               # Pytest test suite
└── utils/
    ├── helpers.py       # utc_now, generate_job_hash, clean_text
    └── logger.py        # Loguru configuration
```

## Key Dependencies

| Package | Purpose |
|---------|---------|
| `fastapi` | Web framework |
| `motor` | Async MongoDB driver |
| `python-jobspy` | Multi-portal job scraping (no login) |
| `apscheduler` | Background task scheduling |
| `passlib` + `python-jose` | Password hashing + JWT |
| `httpx` + `beautifulsoup4` | URL parsing for manual job add |

## Environment Variables

Only infrastructure config needed in `.env`:

```bash
MONGODB_URI=mongodb+srv://...     # Required
MONGODB_DB_NAME=jobpilot          # Required
JWT_SECRET_KEY=your-secret        # Required
```

All user-facing settings (target roles, locations, skills, scrape interval, AI rules, candidate profile) are managed from the UI and stored per-user in MongoDB.

## Testing

```bash
pytest
```
