# JobPilot Frontend

React + Vite + Tailwind CSS dashboard for monitoring and controlling JobPilot.

## Quick Start

```bash
npm install
npm run dev
```

Opens at `http://localhost:5173`. API requests proxy to `http://localhost:8000`.

## Structure

```
frontend/src/
├── main.jsx          → React entry point
├── App.jsx           → Root component + routing
├── index.css         → Tailwind imports + global styles
├── api/client.js     → Axios API client
├── hooks/useApi.js   → Data fetching hook
├── components/       → Reusable UI components
│   ├── Layout.jsx    → App shell (sidebar + content)
│   ├── Sidebar.jsx   → Navigation sidebar
│   ├── JobCard.jsx   → Job listing card
│   ├── StatsCard.jsx → Dashboard metric card
│   ├── MatchScore.jsx→ Circular score indicator
│   ├── StatusBadge.jsx→ Status pill
│   └── EmptyState.jsx→ Empty list placeholder
├── pages/            → Full page components
│   ├── Dashboard.jsx → Overview + charts
│   ├── Jobs.jsx      → Job browser with filters
│   ├── Applications.jsx → Application pipeline
│   ├── ResumeManager.jsx → Resume versions
│   └── Settings.jsx  → Profile + config
└── utils/helpers.js  → Formatting utilities
```

## Pages

- **Dashboard** — Stats cards, timeline chart, portal breakdown, pipeline, activity feed
- **Jobs** — Browse/filter/search all scraped jobs, apply, re-score
- **Applications** — Track application status pipeline with event timeline
- **Resumes** — Upload base resume, view AI-tailored versions, download PDFs
- **Settings** — Profile, scheduler status, portal connections
