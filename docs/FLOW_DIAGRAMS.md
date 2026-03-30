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
        │               (get_user_prefs(user_id))
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

## 2. Manual Job Add Flow

```
User clicks "+ Add Job" on Jobs page
        │
        ▼
Pastes URL → clicks "Fetch"
        │
        ▼
POST /api/jobs/fetch-details
        │
        ▼
job_parser.py fetches URL with httpx
        │
        ├── Try LD+JSON JobPosting schema (Ashby, Greenhouse, Lever)
        ├── Try OpenGraph meta tags (LinkedIn, career pages)
        └── Try <title> tag with platform-specific regex
        │
        ▼
Returns: title, company, location, description, skills
        │
        ▼
Form pre-filled → user reviews → clicks "Add Job"
        │
        ▼
POST /api/jobs/manual → quick score → MongoDB
```

## 3. Resume Tailoring Flow

```
User clicks "Tailor" on a job card
        │
        ▼
POST /api/resumes/tailor?job_id=xxx
        │
        ▼
Fetch: base LaTeX + job description + rules_md + profile_md
(all per-user from MongoDB)
        │
        ▼
Send to Kiro CLI (Claude):
  - System prompt (tailor instructions)
  - Job: title, company, skills, description
  - Rules: user's AI rules from MongoDB
  - Profile: user's candidate profile from MongoDB
  - LaTeX: full resume source
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

## 4. Authentication Flow

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
  └── Extracts user_id — all queries filtered by user_id
```

## 5. Application Tracking Flow

```
User clicks "Apply" on a job card
        │
        ▼
POST /api/applications?job_id=xxx
        │
        ▼
Create application record in MongoDB
        │
        ▼
Update job status to "applied"
        │
        ▼
Job card shows status dropdown (replaces Apply button)
        │
        ▼
User changes status via dropdown OR Kanban drag-and-drop:
  Pending → Applied → Interview → Offered → Accepted
  (both update same applications collection)
        │
        ▼
If status → "Offered" or "Accepted": confetti burst 🎉
```
