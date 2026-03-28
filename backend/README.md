# JobPilot Backend

Python FastAPI backend — API server, job scraping, AI integration, and data management.

## Quick Start

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set up .env (copy from project root)
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
│   ├── jobs.py          # CRUD, scrape trigger, live status, export CSV
│   ├── applications.py  # Application tracking, status updates
│   ├── resumes.py       # LaTeX editor, compile to PDF, AI tailoring
│   ├── dashboard.py     # Stats, timeline, portals, salary insights
│   └── settings.py      # Profile, preferences, rules.md, scheduler
│
├── services/            # Business logic
│   ├── ai_service.py    # Kiro CLI wrapper (no API key needed)
│   ├── resume_tailor.py # AI resume tailoring with rules + profile
│   ├── job_matcher.py   # Quick score (heuristic) + AI score
│   ├── user_prefs.py    # User preferences from MongoDB (not .env)
│   ├── cover_letter_service.py
│   ├── pdf_generator.py
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
├── templates/           # HTML templates for PDF generation
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
| `weasyprint` | HTML → PDF generation |
| `passlib` + `python-jose` | Password hashing + JWT |

## Environment Variables

Only infrastructure config is needed in `.env`:

```bash
MONGODB_URI=mongodb+srv://...     # Required
MONGODB_DB_NAME=jobpilot          # Required
JWT_SECRET_KEY=your-secret        # Required
JWT_ALGORITHM=HS256               # Default
JWT_EXPIRY_HOURS=72               # Default
```

All user-facing settings (target roles, locations, skills, scrape interval) are managed from the UI and stored in MongoDB.

## Testing

```bash
pytest
```
