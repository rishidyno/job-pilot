# JobPilot — Flow Diagrams

## 1. Job Scraping Flow

```
User clicks "Scrape Now" (Dashboard or Jobs page)
        │
        ▼
POST /api/jobs/scrape ──▶ Background task created
        │                        │
        ▼                        ▼
Returns immediately      scraper_manager.scrape_all()
(UI starts polling)              │
        │                        ▼
        │               Load user preferences from MongoDB
        │                        │
        │                        ▼
        │               Expand keywords (synonyms)
        │                        │
        │                        ▼
        │               For each portal × keyword:
        │                   python-jobspy scrape_jobs()
        │                   (runs in thread, non-blocking)
        │                        │
        │                        ▼
        │               For each job found:
        │                   ├── Generate dedup hash
        │                   ├── Quick match score
        │                   ├── Insert to MongoDB (skip dupes)
        │                   ├── Emit live event to status
        │                   └── Telegram alert if high match
        │                        │
        ▼                        ▼
GET /api/jobs/scrape/status     Scrape complete
(polls every 2 seconds)
```

## 2. Resume Tailoring Flow

```
User clicks "Tailor" on a job card
        │
        ▼
POST /api/resumes/tailor?job_id=xxx
        │
        ▼
Fetch base LaTeX resume from MongoDB
        │
        ▼
Fetch job description + skills
        │
        ▼
Send to Kiro CLI (Claude):
  - Base LaTeX + JD + rules.md + profile.md
  - "Modify this LaTeX for this job"
        │
        ▼
AI returns modified LaTeX + changes list
        │
        ▼
Save tailored resume to MongoDB
(with job_title, company, url, score)
        │
        ▼
Re-score the job (quick_score + 5 boost)
        │
        ▼
Return resume_id + changes + new_score
```

## 3. Authentication Flow

```
Register: POST /api/auth/register
  ├── Validate fields (email regex, password strength)
  ├── Hash password (bcrypt)
  ├── Insert user to MongoDB
  ├── Create JWT token
  └── Return token + user

Login: POST /api/auth/login
  ├── Find user by email
  ├── Verify password hash
  ├── Create JWT token
  └── Return token + user

Every API call:
  ├── Frontend: Axios interceptor adds Bearer token
  ├── Backend: Depends(get_current_user_id) validates JWT
  └── Extracts user_id for data isolation
```

## 4. Application Tracking Flow

```
User clicks "Apply" on a job
        │
        ▼
POST /api/applications?job_id=xxx
        │
        ▼
Create application record in MongoDB
  (status: pending, job context, timestamp)
        │
        ▼
Update job status to "applied"
        │
        ▼
Return job URL for manual application
        │
        ▼
User tracks progress via Kanban board:
  Pending → Applied → Interview → Offered → Accepted
  (drag and drop updates status via PATCH)
```
