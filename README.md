<div align="center">

# 🚀 JobPilot

**Your AI-powered job hunting copilot.**

Scrape jobs from LinkedIn, Indeed, Glassdoor & more — tailor your resume with AI — track every application — all from one dashboard.

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)](https://react.dev)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-47A248?logo=mongodb&logoColor=white)](https://mongodb.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[Getting Started](#getting-started) · [Features](#features) · [Screenshots](#screenshots) · [Tech Stack](#tech-stack) · [Contributing](#contributing)

</div>

---

## Why JobPilot?

Job hunting is broken. You spend hours on 6 different portals, manually tailoring resumes, losing track of applications, and missing great opportunities.

JobPilot fixes this:

- **One scrape** pulls jobs from LinkedIn, Indeed, Glassdoor, Google Jobs, and Naukri — no portal accounts needed
- **AI scores** every job against your profile automatically
- **One click** tailors your LaTeX resume for any job description
- **One dashboard** tracks everything from scrape to offer

Self-hosted. Your data stays yours.

---

## Features

### 🔍 Multi-Portal Job Scraping
Powered by [python-jobspy](https://github.com/speedyapply/JobSpy). No login credentials required — uses public APIs.

| Portal | Status | Notes |
|--------|--------|-------|
| LinkedIn | ✅ | Guest API, no login |
| Indeed | ✅ | Supports 40+ countries |
| Glassdoor | ✅ | Reviews + salary data |
| Google Jobs | ✅ | Aggregated results |
| Naukri | ✅ | India-focused, skills + experience |

- Smart keyword expansion (e.g., "Backend Engineer" also searches "Java Developer", "SDE")
- 30-day lookback, 30 results per keyword per portal
- Live scrape monitor with real-time logs
- Configurable scrape scheduling from the UI

### 📄 AI Resume Tailoring
- Write your resume once in LaTeX
- AI rewrites it for each job description — keeping it truthful
- Editable rules (rules.md) control what the AI can and can't change
- Live PDF preview compiled from LaTeX
- Score updates automatically after tailoring

### 📊 Smart Job Matching
- Quick heuristic scoring on every scraped job (skills overlap, location, title relevance)
- AI-powered deep scoring on demand
- Skill match highlighting — see which of YOUR skills match each job
- Score labels: Excellent / Strong / Good / Fair / Weak

### 📋 Application Tracking
- **Kanban board** — drag and drop between Pending → Applied → Interview → Offered → Rejected
- **List view** — expandable cards with timeline, status actions, notes
- **Board/List toggle** — switch views instantly

### 🎯 Job Management
- **Bookmarks** — star jobs to save for later, filter by saved
- **Notes** — add personal context to any job
- **Job comparison** — select 2-3 jobs, compare side-by-side
- **Export CSV** — download all jobs for offline analysis
- **Bulk filters** — by status, portal, score, search text

### 📈 Dashboard & Insights
- Key metrics: total jobs, new today, high matches, applied, interviews
- Jobs-over-time chart
- Per-portal breakdown with distinct colors
- Application pipeline visualization
- Most demanded skills (aggregated from all scraped jobs)
- Salary data table

### ⚙️ Settings & Configuration
- **Profile** — name, email, current role, experience
- **Job preferences** — target roles, locations, skills, experience range (all user-controlled, no .env editing)
- **AI Rules** — markdown editor with live preview for resume generation rules
- **Candidate Profile** — markdown editor for your actual experience/skills
- **Scheduler** — configure scrape interval from the UI
- **Portal status** — see which portals are connected

### 🎨 UI/UX
- **6 Themes** — Light, Dark, Midnight, Nord, Sunset, Emerald
- **Animated landing page** — floating orbs, scroll reveals, typing effect
- **Responsive** — works on desktop and mobile (accessible via WiFi from phone)
- **Keyboard shortcuts** — `g+j` for Jobs, `/` for search, `?` for help
- **Onboarding** — 4-step walkthrough for new users
- **Toast notifications** — replaces all alert() calls
- **Confetti** — celebration burst when status changes to Offered/Accepted
- **Page transitions** — fade-in on mount, scroll progress bar
- **Skeleton loading** — smooth loading states everywhere
- **Focus trapping** — accessible modals
- **Monaco Editor** — VS Code-like LaTeX editing with syntax highlighting
- **Rate limiting** — API protected against brute-force and abuse

---

## Getting Started

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **MongoDB** (Atlas free tier works great)
- **pdflatex** (for LaTeX → PDF compilation)

### 1. Clone & Configure

```bash
git clone https://github.com/rishidyno/job-pilot.git
cd job-pilot
cp .env.example .env
```

Edit `.env` with your MongoDB URI and JWT secret:

```bash
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/?appName=Cluster0
MONGODB_DB_NAME=jobpilot
JWT_SECRET_KEY=your-secret-key-here
GEMINI_API_KEY=your-gemini-api-key
```

> **Note:** Get a free Gemini API key at [aistudio.google.com/apikey](https://aistudio.google.com/apikey). Job portal credentials are NOT required — scraping uses public APIs. All job preferences are configured from the UI after registration.

### 2. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

### 4. Open

- **Dashboard:** http://localhost:5173
- **API Docs:** http://localhost:8000/docs

### Docker (Alternative)

```bash
docker-compose up --build
```

---

## Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| **Frontend** | React 18, Vite, Tailwind CSS | Fast builds, utility-first styling |
| **Backend** | Python, FastAPI | Async, auto-docs, great ecosystem |
| **Database** | MongoDB (Motor async driver) | Flexible schema for varied job data |
| **Scraping** | python-jobspy | Multi-portal, no login, battle-tested |
| **AI** | Google Gemini (gemini-2.5-flash) | Resume tailoring, job scoring, free tier |
| **PDF** | pdflatex | Professional LaTeX resume compilation |
| **Auth** | JWT + bcrypt | Stateless, secure |
| **Charts** | Recharts | Composable React charts |
| **Icons** | Lucide React | Consistent, tree-shakeable |
| **Scheduler** | APScheduler | Background periodic scraping |

---

## Project Structure

```
job-pilot/
├── backend/
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Environment config
│   ├── database.py             # MongoDB connection
│   ├── models/                 # Pydantic schemas
│   ├── routers/                # API endpoints
│   │   ├── auth.py             # Register, login, JWT
│   │   ├── jobs.py             # CRUD, scrape, score, export
│   │   ├── applications.py     # Application tracking
│   │   ├── resumes.py          # LaTeX editor, compile, tailor
│   │   ├── dashboard.py        # Stats, charts, insights
│   │   └── settings.py         # Profile, preferences, rules
│   ├── services/
│   │   ├── ai_service.py       # Google Gemini integration (retry, timeout)
│   │   ├── resume_tailor.py    # AI resume tailoring
│   │   ├── job_matcher.py      # Scoring algorithm
│   │   ├── job_parser.py       # URL parser for manual job add
│   │   └── user_prefs.py       # Per-user preferences from DB
│   ├── scrapers/
│   │   └── scraper_manager.py  # python-jobspy wrapper
│   └── schedulers/
│       └── job_scheduler.py    # APScheduler setup
├── frontend/
│   ├── src/
│   │   ├── pages/              # Home, Dashboard, Jobs, Applications, Resumes, Settings, Login
│   │   ├── components/         # JobCard, KanbanBoard, MarkdownEditor, PdfViewer, AddJobModal, etc.
│   │   ├── hooks/              # useAuth, useApi, useToast, useTheme, useKeyboardShortcuts
│   │   └── api/client.js       # Axios API client
│   └── tailwind.config.js
├── data/
│   ├── rules.md                # AI generation rules (editable from UI)
│   └── profile.md              # Candidate profile (editable from UI)
└── docker-compose.yml
```

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `g` then `d` | Go to Dashboard |
| `g` then `j` | Go to Jobs |
| `g` then `a` | Go to Applications |
| `g` then `r` | Go to Resumes |
| `g` then `s` | Go to Settings |
| `/` | Focus search bar |
| `?` | Show shortcuts help |
| `Esc` | Close modal |

---

## API Overview

Full interactive docs at `http://localhost:8000/docs` (Swagger UI).

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register` | POST | Create account |
| `/api/auth/login` | POST | Get JWT token |
| `/api/jobs` | GET | List jobs (filters, pagination) |
| `/api/jobs/scrape` | POST | Trigger scrape |
| `/api/jobs/scrape/status` | GET | Live scrape status |
| `/api/jobs/manual` | POST | Add job manually (paste URL) |
| `/api/jobs/fetch-details` | POST | Extract job details from URL |
| `/api/jobs/export` | GET | Download CSV |
| `/api/resumes/latex` | GET/PUT | Read/write LaTeX source |
| `/api/resumes/compile/:id` | GET | Compile LaTeX → PDF |
| `/api/resumes/tailor` | POST | AI-tailor resume for a job |
| `/api/dashboard/stats` | GET | Dashboard metrics |
| `/api/dashboard/salary-insights` | GET | Skill demand + salary data |
| `/api/settings/profile` | GET/PUT | User preferences |
| `/api/settings/rules` | GET/PUT | AI rules (markdown) |

---

## Contributing

1. Fork the repo
2. Create a feature branch (`git checkout -b feat/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feat/amazing-feature`)
5. Open a Pull Request

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

<div align="center">

**Built by [Rishi Raj](https://github.com/rishidyno) — because job hunting should be automated.**

</div>
