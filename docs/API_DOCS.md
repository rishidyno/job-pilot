# JobPilot — API Reference

Base URL: `http://localhost:8000`
Interactive Docs: `http://localhost:8000/docs` (Swagger UI)

All endpoints except `/api/auth/register` and `/api/auth/login` require a Bearer token.

## Auth

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Create account (returns JWT) |
| POST | `/api/auth/login` | Login (returns JWT) |
| GET | `/api/auth/me` | Get current user |

## Jobs

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/jobs` | List jobs (filters: status, portal, bookmarked, min_score, search) |
| GET | `/api/jobs/{id}` | Get single job (includes application_id, application_status) |
| PATCH | `/api/jobs/{id}` | Update job (status, notes, bookmarked) |
| DELETE | `/api/jobs/{id}` | Delete job |
| POST | `/api/jobs/{id}/score` | Re-score with AI |
| GET | `/api/jobs/export` | Download all jobs as CSV |
| POST | `/api/jobs/manual` | Add job manually (URL + title + company) |
| POST | `/api/jobs/fetch-details` | Extract job details from any URL |
| POST | `/api/jobs/scrape` | Trigger scrape (optional: portals param) |
| GET | `/api/jobs/scrape/status` | Live scrape status + logs |
| POST | `/api/jobs/scrape/stop` | Stop running scrape |

## Applications

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/applications` | List applications (filter by status) |
| GET | `/api/applications/{id}` | Get application details |
| POST | `/api/applications` | Create application for a job |
| PATCH | `/api/applications/{id}` | Update status/notes |
| POST | `/api/applications/{id}/retry` | Retry failed application |

## Resumes

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/resumes/latex` | Get base LaTeX source |
| PUT | `/api/resumes/latex` | Update base LaTeX source |
| GET | `/api/resumes` | List all resume versions |
| GET | `/api/resumes/{id}` | Get specific resume |
| GET | `/api/resumes/compile/{id}` | Compile LaTeX → PDF (needs token param) |
| POST | `/api/resumes/tailor` | AI-tailor resume for a job |
| POST | `/api/resumes/cover-letter` | Generate cover letter |

## Dashboard

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/dashboard/stats` | Key metrics |
| GET | `/api/dashboard/timeline` | Jobs over time (30 days) |
| GET | `/api/dashboard/portals` | Per-portal breakdown |
| GET | `/api/dashboard/pipeline` | Application pipeline counts |
| GET | `/api/dashboard/recent-activity` | Latest jobs + applications |
| GET | `/api/dashboard/salary-insights` | Salary data + skill demand |

## Settings

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/settings/profile` | Get user profile + preferences |
| PUT | `/api/settings/profile` | Update profile + preferences |
| GET | `/api/settings/scheduler` | Scheduler status |
| POST | `/api/settings/scheduler` | Update scrape interval |
| GET | `/api/settings/portals` | Supported portals (all public, no credentials) |
| GET | `/api/settings/rules` | Get AI rules (per-user, stored in MongoDB) |
| PUT | `/api/settings/rules` | Update AI rules |
| GET | `/api/settings/profile-md` | Get candidate profile (per-user, stored in MongoDB) |
| PUT | `/api/settings/profile-md` | Update candidate profile |
| GET | `/api/settings/health` | Health check |
