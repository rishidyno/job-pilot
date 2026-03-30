# JobPilot — Extension Guide

## Adding a New Job Portal

If python-jobspy supports it, add the portal name to:
1. `SUPPORTED_PORTALS` in `backend/scrapers/scraper_manager.py`
2. `ALL_PORTALS` in `frontend/src/components/ScrapeModal.jsx`
3. Portal colors in `frontend/src/pages/Dashboard.jsx` and `frontend/src/utils/helpers.js`

## Adding a New API Endpoint

1. Create or edit a router in `backend/routers/`
2. Register it in `backend/main.py` with `app.include_router()`
3. Add the API method in `frontend/src/api/client.js`
4. Protect with `user_id: str = Depends(get_current_user_id)` for auth

## Adding a New Frontend Page

1. Create the page in `frontend/src/pages/`
2. Add the route in `App.jsx` inside `ProtectedRoutes` (or as public)
3. Add navigation link in `Sidebar.jsx`
4. Add keyboard shortcut in `useKeyboardShortcuts.jsx`
5. Wrap in `<PageWrapper>` for fade-in animation

## Adding a New Component

Components live in `frontend/src/components/`. Follow existing patterns:
- Dark mode: use `dark:` Tailwind variants
- Responsive: use `sm:` breakpoint
- Accessible: use `aria-label`, `role`, keyboard handlers
- Loading: use `Skeleton` component
- Modals: use `glass-overlay` class for backdrop

## Adding a New Theme

1. Add theme definition in `frontend/src/hooks/useTheme.jsx` THEMES array
2. Add CSS variable overrides in `frontend/src/index.css` under `[data-theme="your-theme"]`
3. Override: surface backgrounds, border colors, brand accent colors

## Modifying AI Behavior

- **Rules**: Edit from Settings UI → stored per-user in MongoDB `user_profile.rules_md`
- **Profile**: Edit from Settings UI → stored per-user in MongoDB `user_profile.profile_md`
- **AI service**: `backend/services/ai_service.py` wraps Kiro CLI
- **Resume tailoring prompt**: `backend/services/resume_tailor.py`
- **Scoring logic**: `backend/services/job_matcher.py`

## Modifying User Preferences

All user-facing config is in MongoDB `user_profile` collection, read via `backend/services/user_prefs.py`. To add a new preference:

1. Add the field to the default profile in `backend/routers/settings.py`
2. Add it to defaults in `backend/services/user_prefs.py`
3. Read it via `get_user_prefs(user_id)` wherever needed
4. Add the UI control in `frontend/src/pages/Settings.jsx`
