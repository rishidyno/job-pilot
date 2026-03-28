# JobPilot Frontend

React 18 + Vite + Tailwind CSS — the dashboard UI for JobPilot.

## Quick Start

```bash
npm install
npm run dev
```

Opens at `http://localhost:5173`. API requests proxy to the backend at `http://localhost:8000`.

## Structure

```
frontend/src/
├── main.jsx                # Entry point (providers: Auth, Toast, Theme, Router)
├── App.jsx                 # Route protection, keyboard shortcuts
├── index.css               # Tailwind + prose styles + animations
│
├── pages/
│   ├── Login.jsx           # Split-screen auth with password strength
│   ├── Dashboard.jsx       # Stats, charts, scrape monitor, salary insights
│   ├── Jobs.jsx            # Job browser with filters, compare, export
│   ├── Applications.jsx    # Kanban board + list view toggle
│   ├── ResumeManager.jsx   # LaTeX editor, PDF preview, tailored versions
│   └── Settings.jsx        # Profile, preferences, rules editor, scheduler
│
├── components/
│   ├── Layout.jsx          # App shell (sidebar + mobile nav)
│   ├── Sidebar.jsx         # Navigation + dark mode toggle + logout
│   ├── JobCard.jsx         # Job listing card (score, skills, salary, freshness)
│   ├── JobDetailModal.jsx  # Full job view with actions
│   ├── JobComparison.jsx   # Side-by-side job comparison table
│   ├── KanbanBoard.jsx     # Drag-and-drop application pipeline
│   ├── MarkdownEditor.jsx  # Edit/preview toggle + fullscreen
│   ├── PdfViewer.jsx       # PDF viewer modal with zoom
│   ├── MatchScore.jsx      # Circular score ring
│   ├── StatsCard.jsx       # Dashboard metric card
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
│   ├── useTheme.jsx        # Dark/light mode toggle
│   ├── useKeyboardShortcuts.jsx  # Global keyboard shortcuts + help modal
│   └── useFocusTrap.js     # Accessible focus trapping for modals
│
├── api/
│   └── client.js           # Axios client with JWT interceptor
│
└── utils/
    └── helpers.js          # timeAgo, scoreColor, scoreLabel, freshness, portalLabel
```

## Key Features

| Feature | Implementation |
|---------|---------------|
| **Dark mode** | `useTheme` hook + Tailwind `dark:` classes |
| **Auth** | JWT stored in localStorage, auto-refresh on mount |
| **Keyboard shortcuts** | `g+d/j/a/r/s` navigation, `/` search, `?` help |
| **Scrape monitor** | Polls `/api/jobs/scrape/status` every 2s, live log feed |
| **Kanban board** | HTML drag-and-drop API, no external library |
| **Job comparison** | Select up to 3 jobs, side-by-side table |
| **Skill matching** | Compares job skills against user's profile skills |
| **PDF preview** | iframe-based with zoom controls |
| **Markdown editor** | react-markdown for preview, monospace textarea for edit |
| **Toast system** | Context-based, animated, auto-dismiss |

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
