# JobPilot — Architecture Deep Dive

## System Overview

JobPilot is a **monorepo** with two main applications (backend + frontend) sharing a MongoDB database. The backend handles all business logic, scraping, AI operations, and auto-apply automation. The frontend is a React dashboard for monitoring and control.

## Data Flow

```
                         ┌──────────────────┐
                         │   User Actions    │
                         │  (Dashboard UI)   │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │   React Frontend  │
                         │   (Vite + TW)     │
                         └────────┬─────────┘
                                  │ HTTP (Axios)
                                  ▼
┌───────────────────────────────────────────────────────────┐
│                    FastAPI Backend                          │
│                                                             │
│  ┌─────────┐  ┌─────────────┐  ┌────────────────────────┐ │
│  │ Routers │──│  Services    │──│  Database (Motor/Mongo) │ │
│  │ (API)   │  │  (Logic)     │  │                        │ │
│  └─────────┘  └──────┬──────┘  └────────────────────────┘ │
│                       │                                     │
│            ┌──────────┼──────────┐                         │
│            │          │          │                         │
│   ┌────────▼──┐ ┌────▼────┐ ┌──▼──────────┐              │
│   │ Scrapers  │ │   AI    │ │  Appliers    │              │
│   │ (6 portals│ │ Service │ │ (Playwright) │              │
│   │ +manager) │ │ (Claude)│ │              │              │
│   └───────────┘ └─────────┘ └──────────────┘              │
│                                                             │
│   ┌─────────────────────────────────────────────────────┐  │
│   │              APScheduler (Background)                │  │
│   │  • Periodic scraping • Auto-apply queue • Telegram  │  │
│   └─────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────┘
```

## Layer Responsibilities

### Routers (`backend/routers/`)
- HTTP endpoint definitions (FastAPI decorators)
- Request validation (via Pydantic models)
- Call services for business logic
- Return JSON responses
- **No business logic here** — routers are thin

### Services (`backend/services/`)
- All business logic lives here
- AI operations (Claude API calls)
- PDF generation
- Telegram notifications
- Resume tailoring algorithms
- Job matching/scoring

### Scrapers (`backend/scrapers/`)
- Each portal has its own scraper class extending `BaseScraper`
- `ScraperManager` orchestrates all scrapers
- Playwright handles browser automation
- Anti-detection: random delays, UA rotation, human-like typing

### Appliers (`backend/appliers/`)
- Mirror structure of scrapers (one per portal)
- Handle the actual form-filling and submission
- Track success/failure with detailed error messages

### Models (`backend/models/`)
- Pydantic models define data shapes
- Used for: API validation, MongoDB documents, internal data passing
- Single source of truth for all data schemas

## Database Schema

### `jobs` Collection
```json
{
  "_id": "ObjectId",
  "title": "SDE-2 Backend",
  "company": "Google",
  "portal": "linkedin",
  "external_id": "3847291056",
  "url": "https://...",
  "description": "Full JD text...",
  "location": "Bengaluru",
  "skills": ["Java", "Spring Boot"],
  "status": "new|reviewed|shortlisted|applied|...",
  "match_score": 85,
  "match_reasoning": "Strong skills match...",
  "job_hash": "sha256...",
  "created_at": "ISODate",
  "updated_at": "ISODate"
}
```

### `applications` Collection
```json
{
  "_id": "ObjectId",
  "job_id": "ref → jobs._id",
  "resume_id": "ref → resumes._id",
  "cover_letter_id": "ref → cover_letters._id",
  "status": "pending|submitted|interview|offered|...",
  "portal": "linkedin",
  "events": [{ "timestamp": "...", "description": "..." }],
  "applied_at": "ISODate"
}
```

### `resumes` Collection
```json
{
  "_id": "ObjectId",
  "is_base": true/false,
  "job_id": "ref → jobs._id (null for base)",
  "raw_text": "Full resume text...",
  "content_json": { "structured resume data" },
  "file_path_original_style": "/data/resumes/...",
  "file_path_clean_style": "/data/resumes/...",
  "changes_made": ["List of AI changes"]
}
```

## Deduplication Strategy

Jobs are deduplicated using a compound unique index on `(portal, external_id)`. When the same job is scraped again, the existing record's `updated_at` timestamp is refreshed instead of creating a duplicate.

## AI Usage Patterns

1. **Quick Score** (heuristic, no API) — Used during bulk scraping for initial filtering
2. **Full AI Score** (Claude API) — Used on-demand for detailed analysis
3. **Resume Tailoring** (Claude API) — Generates tailored content per job
4. **Cover Letter** (Claude API) — Generates personalized cover letters

All AI calls go through `ai_service.py` which tracks token usage.

## Security Notes

- Credentials stored in `.env` (never committed)
- Playwright runs with anti-detection measures
- Rate limiting between scraping actions
- Daily application limits (safety cap)
- No authentication on the API (localhost only — add auth if exposing)
