# JobPilot — Architecture

## System Overview

JobPilot is a monorepo with two applications sharing a MongoDB database:

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

### Resume Tailoring
```
Base LaTeX (MongoDB) + Job Description → Kiro CLI (Claude)
→ Tailored LaTeX → pdflatex → PDF → MongoDB resumes collection
→ Job score updated
```

### Authentication
```
Register/Login → bcrypt hash → JWT token → localStorage
→ Every API call includes Bearer token → FastAPI dependency validates
```

## Key Design Decisions

| Decision | Why |
|----------|-----|
| **python-jobspy over Playwright** | No login needed, 10x faster, doesn't block event loop |
| **Kiro CLI over Anthropic API** | No API key cost, uses existing Claude subscription |
| **User prefs in MongoDB (not .env)** | Multi-user support, no backend access needed |
| **LaTeX for resumes** | Professional output, precise formatting control |
| **APScheduler** | Lightweight, in-process, no external queue needed |
| **JWT (not sessions)** | Stateless, scales horizontally |

## MongoDB Collections

| Collection | Purpose |
|------------|---------|
| `users` | Auth credentials (email, password_hash) |
| `user_profile` | Preferences, target roles, skills |
| `jobs` | Scraped job listings |
| `resumes` | Base LaTeX + tailored versions |
| `applications` | Application tracking + events |
| `cover_letters` | Generated cover letters |
| `scrape_logs` | Scrape run history |

## Frontend Architecture

```
main.jsx
├── ThemeProvider (dark/light mode)
├── ToastProvider (notifications)
├── AuthProvider (JWT + user state)
└── App.jsx
    ├── /login → Login (public)
    └── /* → ProtectedRoutes
        ├── Layout (Sidebar + content)
        ├── KeyboardShortcuts (global)
        └── Pages (Dashboard, Jobs, Applications, Resumes, Settings)
```

Components are self-contained with their own modals (JobDetailModal, PdfViewer, ConfirmDialog). State management uses React hooks — no Redux or external state library.
