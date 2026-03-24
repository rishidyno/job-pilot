# 🚀 JobPilot — AI-Powered Automated Job Application Engine

> A self-hosted, intelligent job hunting tool that scrapes jobs from multiple portals, tailors your resume & cover letter using Claude AI, tracks every application in MongoDB, and auto-applies — all from a beautiful dashboard.

**Built for:** Rishi Raj — Backend/Full-Stack SDE-1/2 roles with 1.5-2 YOE  
**Target locations:** Bengaluru, Remote, Hyderabad, Noida, Gurgaon

---

## 📋 Table of Contents

- [Architecture Overview](#architecture-overview)
- [Tech Stack](#tech-stack)
- [Features](#features)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Extending JobPilot](#extending-jobpilot)
- [Flow Diagrams](#flow-diagrams)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     JOBPILOT ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐   │
│  │   React +     │    │   FastAPI     │    │   MongoDB        │   │
│  │   Vite +      │◄──►│   Backend     │◄──►│   Database       │   │
│  │   Tailwind    │    │   (REST API)  │    │   (jobs, apps,   │   │
│  │   Dashboard   │    │              │    │    resumes)       │   │
│  └──────────────┘    └──────┬───────┘    └──────────────────┘   │
│                              │                                    │
│           ┌──────────────────┼──────────────────┐                │
│           │                  │                  │                │
│  ┌────────▼──────┐  ┌───────▼───────┐  ┌──────▼──────────┐    │
│  │  Job Scrapers  │  │  AI Services  │  │  Auto-Appliers  │    │
│  │  ─────────────│  │  ────────────│  │  ──────────────│    │
│  │  • LinkedIn    │  │  • Claude API │  │  • LinkedIn     │    │
│  │  • Naukri      │  │  • Resume     │  │  • Naukri       │    │
│  │  • Wellfound   │  │    Tailoring  │  │  • Wellfound    │    │
│  │  • Instahyre   │  │  • Cover      │  │  • Instahyre    │    │
│  │  • Indeed      │  │    Letters    │  │  • Indeed        │    │
│  │  • Glassdoor   │  │  • Job Match  │  │  • Glassdoor     │    │
│  │  • Extensible  │  │    Scoring    │  │  • Extensible    │    │
│  └───────────────┘  └──────────────┘  └────────────────┘    │
│           │                                     │                │
│  ┌────────▼─────────────────────────────────────▼───────────┐   │
│  │              Playwright Browser Automation                │   │
│  │              (Headless Chrome for form-filling)           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                    │
│  ┌───────────────────────────▼──────────────────────────────┐   │
│  │              Background Scheduler (APScheduler)           │   │
│  │  • Periodic job scraping    • Auto-apply queue            │   │
│  │  • Match scoring updates    • Telegram notifications      │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer           | Technology                              | Why                                      |
|-----------------|----------------------------------------|------------------------------------------|
| **Backend**     | Python 3.11+ / FastAPI                 | Best ecosystem for scraping + AI + PDF   |
| **Frontend**    | React 18 / Vite / Tailwind CSS         | Fast, modern, great for dashboards       |
| **Database**    | MongoDB (via Motor async driver)       | Flexible schema for varied job data      |
| **AI Engine**   | Anthropic Claude API (claude-sonnet-4-20250514) | Resume tailoring + cover letters     |
| **Scraping**    | Playwright + BeautifulSoup             | Reliable browser automation + parsing    |
| **PDF Gen**     | WeasyPrint + Jinja2 templates          | Professional PDF resume output           |
| **Scheduler**   | APScheduler                            | Background job scraping & auto-apply     |
| **Notifications** | python-telegram-bot                  | Real-time Telegram alerts                |

---

## Features

### Core Features
- ✅ **Multi-portal job scraping** — LinkedIn, Naukri, Wellfound, Instahyre, Indeed, Glassdoor
- ✅ **AI-powered resume tailoring** — Claude generates two versions (original format + clean template)
- ✅ **Cover letter generation** — Tailored per job description
- ✅ **Smart job matching** — AI scores each job against your profile (0-100)
- ✅ **Dual-mode auto-apply** — Full-auto or semi-auto (review before applying)
- ✅ **Application tracking** — Every application tracked with status pipeline
- ✅ **Dashboard** — Beautiful React UI showing all jobs, stats, and application status
- ✅ **Telegram bot** — Instant notifications for high-match jobs

### Technical Features
- ✅ Modular scraper architecture — add new portals by extending `BaseScraper`
- ✅ Modular applier architecture — add new auto-appliers by extending `BaseApplier`
- ✅ Background scheduler for periodic scraping
- ✅ Deduplication — same job from multiple portals won't create duplicates
- ✅ Rate limiting & anti-detection for scraping
- ✅ Comprehensive API with auto-generated OpenAPI docs
- ✅ Base resume always preserved — tailored versions are derivatives

---

## Project Structure

```
job-pilot/
├── README.md                          # You are here
├── docker-compose.yml                 # MongoDB + app containers
├── .env.example                       # Environment variables template
├── Makefile                           # Common commands
│
├── backend/                           # ═══ PYTHON FASTAPI BACKEND ═══
│   ├── README.md                      # Backend-specific docs
│   ├── requirements.txt               # Python dependencies
│   ├── main.py                        # FastAPI app entry point & lifespan
│   ├── config.py                      # Centralized config from env vars
│   ├── database.py                    # MongoDB connection (async Motor)
│   │
│   ├── models/                        # ── Pydantic models (data shapes) ──
│   │   ├── __init__.py
│   │   ├── job.py                     # Job listing schema
│   │   ├── application.py             # Application tracking schema
│   │   ├── resume.py                  # Resume & cover letter schema
│   │   └── user_profile.py            # Your profile/preferences
│   │
│   ├── routers/                       # ── API route handlers ──
│   │   ├── __init__.py
│   │   ├── jobs.py                    # /api/jobs/* endpoints
│   │   ├── applications.py            # /api/applications/* endpoints
│   │   ├── resumes.py                 # /api/resumes/* endpoints
│   │   ├── dashboard.py               # /api/dashboard/* (stats/analytics)
│   │   └── settings.py                # /api/settings/* endpoints
│   │
│   ├── services/                      # ── Business logic layer ──
│   │   ├── __init__.py
│   │   ├── ai_service.py             # Claude API client wrapper
│   │   ├── resume_tailor.py          # Resume tailoring with AI
│   │   ├── cover_letter_service.py   # Cover letter generation
│   │   ├── job_matcher.py            # Job-profile match scoring
│   │   ├── telegram_service.py       # Telegram bot notifications
│   │   └── pdf_generator.py          # PDF resume/cover letter gen
│   │
│   ├── scrapers/                      # ── Job portal scrapers ──
│   │   ├── __init__.py
│   │   ├── base_scraper.py           # Abstract base class (extend this!)
│   │   ├── linkedin_scraper.py       # LinkedIn Jobs scraper
│   │   ├── naukri_scraper.py         # Naukri.com scraper
│   │   ├── wellfound_scraper.py      # Wellfound (AngelList) scraper
│   │   ├── instahyre_scraper.py      # Instahyre scraper
│   │   ├── indeed_scraper.py         # Indeed scraper
│   │   ├── glassdoor_scraper.py      # Glassdoor scraper
│   │   └── scraper_manager.py        # Orchestrator for all scrapers
│   │
│   ├── appliers/                      # ── Auto-apply modules ──
│   │   ├── __init__.py
│   │   ├── base_applier.py           # Abstract base class (extend this!)
│   │   ├── linkedin_applier.py       # LinkedIn Easy Apply automation
│   │   ├── naukri_applier.py         # Naukri apply automation
│   │   ├── wellfound_applier.py      # Wellfound apply automation
│   │   ├── instahyre_applier.py      # Instahyre apply automation
│   │   └── applier_manager.py        # Orchestrator for all appliers
│   │
│   ├── schedulers/                    # ── Background tasks ──
│   │   ├── __init__.py
│   │   └── job_scheduler.py          # APScheduler setup & task definitions
│   │
│   ├── templates/                     # ── Jinja2 HTML templates ──
│   │   ├── resume_original.html      # Resume template matching your style
│   │   └── resume_clean.html         # Clean professional template
│   │
│   └── utils/                         # ── Shared utilities ──
│       ├── __init__.py
│       ├── logger.py                  # Structured logging setup
│       └── helpers.py                 # Common helper functions
│
├── frontend/                          # ═══ REACT + VITE FRONTEND ═══
│   ├── README.md                      # Frontend-specific docs
│   ├── package.json                   # Node dependencies
│   ├── vite.config.js                 # Vite configuration
│   ├── tailwind.config.js             # Tailwind CSS config
│   ├── postcss.config.js              # PostCSS config
│   ├── index.html                     # HTML entry point
│   └── src/
│       ├── main.jsx                   # React entry point
│       ├── App.jsx                    # Root component with routing
│       ├── api/
│       │   └── client.js             # Axios API client
│       ├── components/                # Reusable UI components
│       │   ├── Layout.jsx            # App shell (sidebar + content)
│       │   ├── Sidebar.jsx           # Navigation sidebar
│       │   ├── JobCard.jsx           # Job listing card
│       │   ├── StatusBadge.jsx       # Application status pill
│       │   ├── StatsCard.jsx         # Dashboard metric card
│       │   ├── MatchScore.jsx        # Visual match score indicator
│       │   └── EmptyState.jsx        # Empty state placeholder
│       ├── pages/                     # Page-level components
│       │   ├── Dashboard.jsx         # Overview with stats & charts
│       │   ├── Jobs.jsx              # Job listings browser
│       │   ├── Applications.jsx      # Application tracker pipeline
│       │   ├── ResumeManager.jsx     # Resume versions manager
│       │   └── Settings.jsx          # App configuration
│       ├── hooks/
│       │   └── useApi.js             # Custom hook for API calls
│       └── utils/
│           └── helpers.js            # Frontend utility functions
│
├── data/                              # ═══ LOCAL DATA STORAGE ═══
│   ├── resumes/                       # Base + tailored resume PDFs
│   └── cover_letters/                 # Generated cover letter PDFs
│
└── docs/                              # ═══ DOCUMENTATION ═══
    ├── ARCHITECTURE.md                # Detailed architecture deep-dive
    ├── API_DOCS.md                    # Full API reference
    ├── FLOW_DIAGRAMS.md               # User flows & data flows
    ├── SCRAPER_GUIDE.md               # How to add new scrapers
    └── EXTENDING.md                   # How to extend JobPilot
```

---

## Setup & Installation

### Prerequisites
- Python 3.11+
- Node.js 18+
- MongoDB 6+ (or use Docker)
- Chrome/Chromium (for Playwright)
- Anthropic API key

### Quick Start

```bash
# 1. Clone the repository
git clone <your-repo-url> job-pilot
cd job-pilot

# 2. Copy and edit environment variables
cp .env.example .env
# Edit .env with your API keys (see Configuration section)

# 3. Start MongoDB (via Docker)
docker-compose up -d mongodb

# 4. Install backend dependencies
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium

# 5. Install frontend dependencies
cd ../frontend
npm install

# 6. Copy your base resume
cp /path/to/your/resume.pdf ../data/resumes/base_resume.pdf

# 7. Start the backend
cd ../backend
uvicorn main:app --reload --port 8000

# 8. Start the frontend (new terminal)
cd ../frontend
npm run dev
```

Open **http://localhost:5173** for the dashboard.  
API docs at **http://localhost:8000/docs** (Swagger UI).

### Docker Start (Alternative)

```bash
cp .env.example .env
# Edit .env with your keys
docker-compose up --build
```

---

## Configuration

All configuration is via environment variables (`.env` file):

```bash
# ═══ REQUIRED ═══
ANTHROPIC_API_KEY=sk-ant-...          # Your Claude API key
MONGODB_URI=mongodb://localhost:27017  # MongoDB connection string
MONGODB_DB_NAME=jobpilot               # Database name

# ═══ JOB SEARCH PREFERENCES ═══
TARGET_ROLE=Backend Engineer,Full Stack Developer,SDE-1,SDE-2,Software Engineer
TARGET_EXPERIENCE_MIN=1.5
TARGET_EXPERIENCE_MAX=2.5
TARGET_LOCATIONS=Bengaluru,Remote,Hyderabad,Noida,Gurgaon

# ═══ TELEGRAM (optional) ═══
TELEGRAM_BOT_TOKEN=                    # From @BotFather
TELEGRAM_CHAT_ID=                      # Your chat ID

# ═══ JOB PORTAL CREDENTIALS ═══
LINKEDIN_EMAIL=
LINKEDIN_PASSWORD=
NAUKRI_EMAIL=
NAUKRI_PASSWORD=
WELLFOUND_EMAIL=
WELLFOUND_PASSWORD=
INSTAHYRE_EMAIL=
INSTAHYRE_PASSWORD=

# ═══ SCHEDULER ═══
SCRAPE_INTERVAL_HOURS=6                # How often to scrape
AUTO_APPLY_ENABLED=false               # Master switch for auto-apply
AUTO_APPLY_MODE=semi                   # "auto" or "semi"
MIN_MATCH_SCORE_TO_APPLY=70            # Only apply if match >= this

# ═══ ADVANCED ═══
LOG_LEVEL=INFO
PLAYWRIGHT_HEADLESS=true               # Set false to see browser
```

---

## API Documentation

Interactive API docs available at `http://localhost:8000/docs` when running.

See [docs/API_DOCS.md](docs/API_DOCS.md) for the complete API reference.

---

## Flow Diagrams

See [docs/FLOW_DIAGRAMS.md](docs/FLOW_DIAGRAMS.md) for detailed user & data flows.

---

## Extending JobPilot

### Adding a New Job Portal Scraper
See [docs/SCRAPER_GUIDE.md](docs/SCRAPER_GUIDE.md) — just extend `BaseScraper`!

### Adding a New Auto-Applier
Same pattern — extend `BaseApplier` in `backend/appliers/`.

### Full Extension Guide
See [docs/EXTENDING.md](docs/EXTENDING.md).

---

## License

Personal project — not for redistribution.

---

**Built with ❤️ by Rishi Raj — because job hunting should be automated.**
