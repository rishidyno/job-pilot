# JobPilot — Architecture

## System Overview

```
┌─────────────┐     ┌──────────────┐     ┌───────────┐
│  React SPA  │────▶│  FastAPI      │────▶│  MongoDB  │
│  (Vite)     │     │  (uvicorn)   │     │  (Atlas)  │
│  Port 5173  │     │  Port 8000   │     │  Cloud    │
└─────────────┘     └──────┬───────┘     └───────────┘
                           │
                    ┌──────┴───────┐
                    │  python-     │
                    │  jobspy      │
                    │  (httpx)     │
                    └──────────────┘
```

## Data Flow

### Scraping
```
User preferences (MongoDB) → keyword expansion → python-jobspy
→ DataFrame → dedup + score → MongoDB jobs collection
→ Telegram notification (if high match)
```

### Manual Job Add
```
User pastes URL → POST /api/jobs/fetch-details
→ httpx fetches page → parse LD+JSON / OG tags / <title>
→ Pre-fill form → user reviews → POST /api/jobs/manual
→ Quick score → MongoDB
```

### Resume Tailoring
```
Base LaTeX (MongoDB) + Job Description + rules_md + profile_md
→ Kiro CLI (Claude) → Tailored LaTeX
→ pdflatex → PDF → MongoDB resumes collection
→ Job score updated
```

### Authentication
```
Register/Login → bcrypt hash → JWT token → localStorage
→ Every API call includes Bearer token
→ FastAPI dependency validates + extracts user_id
→ All data queries filtered by user_id
```

## Key Design Decisions

| Decision | Why |
|----------|-----|
| **python-jobspy over Playwright** | No login needed, 10x faster, doesn't block event loop |
| **Kiro CLI over Anthropic API** | No API key cost, uses existing Claude subscription |
| **User prefs in MongoDB (not .env)** | Multi-user support, no backend access needed |
| **Rules + profile per user in MongoDB** | Multi-user isolation, not shared files on disk |
| **LaTeX for resumes** | Professional output, precise formatting control |
| **APScheduler** | Lightweight, in-process, no external queue needed |
| **JWT (not sessions)** | Stateless, scales horizontally |
| **6 themes via CSS variables** | No Tailwind config changes, instant switching |

## MongoDB Collections

| Collection | Purpose |
|------------|---------|
| `users` | Auth credentials (email, password_hash) |
| `user_profile` | Preferences, target roles, skills, rules_md, profile_md |
| `jobs` | Scraped + manually added job listings |
| `resumes` | Base LaTeX + tailored versions |
| `applications` | Application tracking + events |
| `cover_letters` | Generated cover letters |
| `scrape_logs` | Scrape run history |

## Frontend Architecture

```
main.jsx
├── ThemeProvider (6 themes via CSS variables)
├── ToastProvider (notifications)
├── AuthProvider (JWT + user state)
└── App.jsx
    ├── / → Home (public landing page)
    ├── /login → Login (public)
    └── /* → ProtectedRoutes
        ├── Layout (Sidebar + content)
        ├── KeyboardShortcuts (global)
        └── Pages (Dashboard, Jobs, Applications, Resumes, Settings)
```

## Scoring System

### Quick Score (heuristic, no AI)
- Skills overlap: up to 50 points
- Location match: up to 20 points
- Title relevance: up to 30 points
- Runs on every scraped job instantly

### AI Score (Claude via Kiro CLI)
- Skills Match: 35%
- Experience Fit: 25%
- Role Alignment: 20%
- Location Match: 10%
- Growth Potential: 10%
- Runs on demand when user clicks "Score"
