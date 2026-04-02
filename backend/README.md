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
├── main.py              # FastAPI app, lifespan, CORS, rate limiting
├── config.py            # Pydantic settings from .env
├── database.py          # MongoDB async connection + indexes
│
├── routers/
│   ├── auth.py          # Register, login, JWT (rate limited: 5/min login, 3/min register)
│   ├── jobs.py          # CRUD, scrape, score, export CSV, manual add, fetch URL
│   ├── applications.py  # Application tracking, status updates
│   ├── resumes.py       # LaTeX editor, compile to PDF (local or remote), AI tailoring
│   ├── dashboard.py     # Stats (cached 60s), timeline, portals, salary insights
│   └── settings.py      # Profile, preferences, rules, scheduler, portals
│
├── services/
│   ├── ai_service.py    # Google Gemini API (retry, timeout, error isolation)
│   ├── resume_tailor.py # AI resume tailoring with per-user rules + profile
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
├── defaults/            # Template files for new users (rules.md, profile.md)
├── tests/               # 82 tests (pytest + mongomock-motor)
└── utils/
    ├── helpers.py       # utc_now, generate_job_hash, valid_oid
    └── logger.py        # Loguru configuration
```

## Security

- Rate limiting via slowapi (global 60/min, login 5/min, register 3/min)
- JWT auth on all endpoints (except register/login)
- ObjectId validation via `valid_oid()` helper (consistent 400 errors)
- Search input escaped with `re.escape()` (prevents ReDoS)
- CORS restricted to specific Vercel domains
- Startup warning if JWT secret is default value

## Environment Variables

```bash
MONGODB_URI=mongodb+srv://...     # Required
MONGODB_DB_NAME=jobpilot          # Required
JWT_SECRET_KEY=your-secret        # Required (change from default!)
GEMINI_API_KEY=your-key           # Required for AI features
```

## Testing

```bash
pytest                    # Run all 82 tests
pytest -x -q              # Stop on first failure, quiet output
```
