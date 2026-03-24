# JobPilot Backend

Python FastAPI backend powering all of JobPilot's functionality.

## Quick Start

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# Make sure MongoDB is running
uvicorn main:app --reload --port 8000
```

## Structure

```
backend/
├── main.py           → FastAPI app entry point
├── config.py         → Settings from .env
├── database.py       → MongoDB connection (async Motor)
├── models/           → Pydantic schemas
├── routers/          → API endpoints
├── services/         → Business logic (AI, PDF, Telegram)
├── scrapers/         → Job portal scrapers (Playwright)
├── appliers/         → Auto-apply modules (Playwright)
├── schedulers/       → Background tasks (APScheduler)
├── templates/        → HTML templates for PDF generation
└── utils/            → Logger, helpers
```

## API Docs

Start the server, then visit: `http://localhost:8000/docs`

## Key Environment Variables

- `ANTHROPIC_API_KEY` — Required for AI features
- `MONGODB_URI` — MongoDB connection (default: localhost:27017)
- `PLAYWRIGHT_HEADLESS` — Set `false` to watch browser during scraping
