# JobPilot Frontend

React 18 + Vite + Tailwind CSS — the dashboard UI for JobPilot.

## Quick Start

```bash
npm install
npm run dev
```

Opens at `http://localhost:5173`. Accessible from phone on same WiFi. API proxied to `http://127.0.0.1:8000`.

## Structure

```
frontend/src/
├── main.jsx                # Entry point (providers: Auth, Toast, Theme, Router)
├── App.jsx                 # Route protection, keyboard shortcuts
├── index.css               # Tailwind + 6 themes + animations
│
├── pages/
│   ├── Home.jsx            # Public landing page (animated, scroll reveals)
│   ├── Login.jsx           # Auth with password strength, dark animated
│   ├── Dashboard.jsx       # Stats (cached), charts, scrape monitor, salary insights
│   ├── Jobs.jsx            # Job browser with filters, compare, export, manual add
│   ├── Applications.jsx    # Kanban board + list view, confetti on offers
│   ├── ResumeManager.jsx   # Monaco LaTeX editor, PDF preview, tailored versions
│   └── Settings.jsx        # Profile, preferences, markdown editors, scheduler
│
├── components/
│   ├── LatexEditor.jsx     # Monaco Editor (VS Code) for LaTeX
│   ├── JobCard.jsx         # Job card (score, skills match, salary, status selector)
│   ├── KanbanBoard.jsx     # Drag-and-drop application pipeline
│   ├── AddJobModal.jsx     # Paste URL → auto-fetch → review → add
│   ├── MarkdownEditor.jsx  # Edit/preview toggle + fullscreen
│   ├── PdfViewer.jsx       # PDF viewer modal with zoom
│   ├── JobComparison.jsx   # Side-by-side job comparison table
│   ├── JobDetailModal.jsx  # Full job view with actions
│   ├── Animations.jsx      # PageWrapper, ScrollProgress
│   ├── Confetti.jsx        # Celebration particles on offers
│   ├── Layout.jsx          # App shell (sidebar + mobile nav)
│   ├── Sidebar.jsx         # Navigation + 6-theme picker + logout
│   ├── ScrapeModal.jsx     # Portal selector for scraping
│   ├── OnboardingModal.jsx # 4-step new user walkthrough
│   ├── ConfirmDialog.jsx   # Accessible confirmation dialog
│   ├── EmptyState.jsx      # Contextual empty state with presets
│   ├── Skeleton.jsx        # Loading placeholders (dark mode aware)
│   ├── MatchScore.jsx      # Circular score ring
│   ├── StatsCard.jsx       # Dashboard metric card
│   └── StatusBadge.jsx     # Colored status pill
│
├── hooks/
│   ├── useAuth.jsx         # Auth context (login, register, logout, token)
│   ├── useApi.js           # Data fetching with loading/error states
│   ├── useToast.jsx        # Toast notification system
│   ├── useTheme.jsx        # 6 themes (Light, Dark, Midnight, Nord, Sunset, Emerald)
│   ├── useKeyboardShortcuts.jsx  # Global shortcuts + help modal
│   └── useFocusTrap.js     # Accessible focus trapping for modals
│
├── api/client.js           # Axios client with JWT interceptor
└── utils/helpers.js        # timeAgo, scoreColor, scoreLabel, freshness, portalLabel
```

## Key Features

| Feature | Implementation |
|---------|---------------|
| **6 Themes** | CSS variables per data-theme attribute |
| **Monaco Editor** | VS Code-like LaTeX editing with syntax highlighting |
| **Split PDF Preview** | Side-by-side LaTeX editor + compiled PDF |
| **Kanban Board** | HTML drag-and-drop, no external library |
| **Job Comparison** | Select up to 3 jobs, side-by-side table |
| **Manual Job Add** | Paste URL → auto-extract via LD+JSON/OG tags |
| **App Status on Card** | Dropdown selector syncs with Kanban |
| **Confetti** | Celebration burst on Offered/Accepted |
| **Page Transitions** | Fade-in on mount, scroll progress bar |
| **Keyboard Shortcuts** | `g+d/j/a/r/s` navigation, `/` search, `?` help |
