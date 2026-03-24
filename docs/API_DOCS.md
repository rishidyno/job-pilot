# JobPilot — API Reference

Base URL: `http://localhost:8000`  
Interactive Docs: `http://localhost:8000/docs` (Swagger UI)

---

## Jobs

### `GET /api/jobs`
List jobs with filtering, sorting, and pagination.

**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| status | string | — | Filter: new, reviewed, shortlisted, applied, etc. |
| portal | string | — | Filter: linkedin, naukri, wellfound, etc. |
| min_score | int | — | Minimum match score (0-100) |
| search | string | — | Full-text search in title, company, description |
| sort_by | string | match_score | Sort field: match_score, created_at, title |
| sort_order | string | desc | Sort direction: asc or desc |
| skip | int | 0 | Pagination offset |
| limit | int | 50 | Page size (max 200) |

**Response:** `{ jobs: [...], total: int, skip: int, limit: int, has_more: bool }`

### `GET /api/jobs/:id`
Get a single job with full details.

### `PATCH /api/jobs/:id`
Update a job's status, notes, or apply mode.

**Body:** `{ status?, match_score?, notes?, apply_mode? }`

### `DELETE /api/jobs/:id`
Delete a job from the database.

### `POST /api/jobs/scrape`
Trigger a manual scrape run (runs in background).

**Query:** `portals=linkedin,naukri` (optional — defaults to all)

### `POST /api/jobs/:id/score`
Re-score a job using full AI analysis (Claude API call).

---

## Applications

### `GET /api/applications`
List all applications with optional status filter.

### `GET /api/applications/:id`
Get application details including event timeline.

### `POST /api/applications`
Apply to a job — triggers the full pipeline (tailor resume → generate cover letter → auto-apply).

**Query:** `job_id=string&force=bool`

### `PATCH /api/applications/:id`
Update status or notes.

**Query:** `status=string&notes=string`

### `POST /api/applications/:id/retry`
Retry a failed application.

---

## Resumes

### `POST /api/resumes/upload-base`
Upload your base resume (PDF, multipart/form-data).

### `GET /api/resumes`
List all resume versions (base + tailored).

### `POST /api/resumes/tailor`
Generate a tailored resume for a specific job.

**Query:** `job_id=string`

### `POST /api/resumes/cover-letter`
Generate a cover letter for a specific job.

**Query:** `job_id=string&tone=professional|enthusiastic|concise`

### `GET /api/resumes/download/:id`
Download a resume PDF.

**Query:** `style=original|clean`

---

## Dashboard

### `GET /api/dashboard/stats`
Key metrics: total jobs, new today, applied, interviews, offers, avg score.

### `GET /api/dashboard/pipeline`
Application pipeline counts per status.

### `GET /api/dashboard/portals`
Per-portal breakdown (total jobs, avg score, high matches).

### `GET /api/dashboard/timeline`
Daily job counts for the past 30 days (for charting).

### `GET /api/dashboard/recent-activity`
10 most recent actions (jobs found, applications).

---

## Settings

### `GET /api/settings/profile`
Get user profile and preferences.

### `PUT /api/settings/profile`
Update profile and preferences.

### `GET /api/settings/scheduler`
Get scheduler status and upcoming jobs.

### `GET /api/settings/portals`
Get connection status for all supported portals.

### `GET /api/settings/health`
Health check with AI token usage stats.
