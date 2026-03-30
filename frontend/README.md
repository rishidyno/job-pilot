# JobPilot Frontend

React 18 + Vite + Tailwind CSS — the dashboard UI for JobPilot.

## Quick Start

```bash
npm install
npm run dev
```

Opens at `http://localhost:5173`. Accessible from phone on same WiFi. API requests proxy to `http://127.0.0.1:8000`.

## Structure

```
frontend/src/
├── main.jsx                # Entry point (providers: Auth, Toast, Theme, Router)
├── App.jsx                 # Route protection, keyboard shortcuts
├── index.css               # Tailwind + themes + animations
│
├── pages/
│   ├── Home.jsx            # Public landing page (animated, scroll reveals)
│   ├── Login.jsx           # Auth with password strength, dark animated
│   ├── Dashboard.jsx       # Stats, charts, scrape monitor, salary insights
│   ├── Jobs.jsx            # Job browser with filters, compare, export, manual add
│   ├── Applications.jsx    # Kanban board + list view, confetti on offers
│   ├── ResumeManager.jsx   # LaTeX editor, PDF preview, tailored versions
│   └── Settings.jsx        # Profile, preferences, markdown editors, scheduler
│
├── components/
│   ├── Layout.jsx          # App shell (sidebar + mobile nav)
│   ├── Sidebar.jsx         # Navigation + 6-theme picker + logout
│   ├── JobCard.jsx         # Job card (score, skills match, salary, status selector)
│   ├── JobDetailModal.jsx  # Full job view with actions
│   ├── JobComparison.jsx   # Side-by-side job comparison table
│   ├── AddJobModal.jsx     # Paste URL → auto-fetch → review → add
│   ├── KanbanBoard.jsx     # Drag-and-drop application pipeline
│   ├── MarkdownEditor.jsx  # Edit/preview toggle + fullscreen
│   ├── PdfViewer.jsx       # PDF viewer modal with zoom
│   ├── Animations.jsx      # PageWrapper, ScrollProgress
│   ├── Confetti.jsx        # Celebration particles on offers
│   ├── MatchScore.jsx      # Circular score ring
│   ├── StatsCard.jsx       # Dashboard metric card with hover lift
│   ├── StatusBadge.jsx     # Colored status pill
│   ├── ScrapeModal.jsx     # Portal selector for scraping
│   ├── OnboardingModal.jsx # 4-step new user walkthrough
│   ├── ConfirmDialog.jsx   # Accessible confirmation dialog
│   ├── EmptyState.jsx      # Contextual empty state with presets
│   └── Skeleton.jsx        # Loading placeholders (dark mode aware)
│
├── hooks/
│   ├── useAuth.jsx         # Auth context (login, register, logout, token)
│   ├── useApi.js           # Data fetching with loading/error states
│   ├── useToast.jsx        # Toast notification system
│   ├── useTheme.jsx        # 6 themes (Light, Dark, Midnight, Nord, Sunset, Emerald)
│   ├── useKeyboardShortcuts.jsx  # Global shortcuts + help modal
│   └── useFocusTrap.js     # Accessible focus trapping for modals
│
├── api/
│   └── client.js           # Axios client with JWT interceptor
│
└── utils/
    └── helpers.js          # timeAgo, scoreColor, scoreLabel, freshness, portalLabel
```

## Routes

| Path | Auth | Page |
|------|------|------|
| `/` | Public | Animated landing page |
| `/login` | Public | Login / Register |
| `/dashboard` | Required | Dashboard with stats and charts |
| `/jobs` | Required | Job browser |
| `/applications` | Required | Kanban board |
| `/resumes` | Required | LaTeX editor + tailored versions |
| `/settings` | Required | Profile, preferences, AI rules |

## Key Features

| Feature | Implementation |
|---------|---------------|
| **6 Themes** | Light, Dark, Midnight, Nord, Sunset, Emerald via CSS variables |
| **Auth** | JWT in localStorage, auto-refresh on mount |
| **Keyboard shortcuts** | `g+d/j/a/r/s` navigation, `/` search, `?` help |
| **Scrape monitor** | Polls status every 2s, live log feed |
| **Kanban board** | HTML drag-and-drop, no external library |
| **Job comparison** | Select up to 3 jobs, side-by-side table |
| **Skill matching** | Compares job skills against user's profile |
| **Manual job add** | Paste URL → auto-extract title/company/skills |
| **App status on card** | Dropdown selector syncs with Kanban |
| **PDF preview** | iframe with zoom controls |
| **Markdown editor** | react-markdown preview, fullscreen mode |
| **Confetti** | Celebration burst on Offered/Accepted status |
| **Page transitions** | Fade-in on mount, scroll progress bar |

## Dependencies

| Package | Purpose |
|---------|---------|
| `react` + `react-dom` | UI framework |
| `react-router-dom` | Client-side routing |
| `axios` | HTTP client with interceptors |
| `recharts` | Dashboard charts |
| `react-markdown` | Markdown preview rendering |
| `lucide-react` | Icon library |
| `clsx` | Conditional class names |
| `date-fns` | Date formatting |
| `tailwindcss` | Utility-first CSS |
| `vite` | Build tool + dev server + proxy |
