# JobPilot — Flow Diagrams

## 1. Job Scraping Flow

```
User clicks "Scrape Now"          Scheduler triggers every N hours
        │                                    │
        └──────────────┬─────────────────────┘
                       ▼
              ┌─────────────────┐
              │ ScraperManager  │
              │ .scrape_all()   │
              └────────┬────────┘
                       │
          ┌────────────┼────────────┬────────────┐
          ▼            ▼            ▼            ▼
    ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
    │ LinkedIn │ │  Naukri   │ │Wellfound │ │  Indeed  │ ...
    │ Scraper  │ │ Scraper  │ │ Scraper  │ │ Scraper  │
    └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘
         │            │            │            │
         └────────────┼────────────┼────────────┘
                      ▼
         ┌─────────────────────────┐
         │  For each scraped job:  │
         │  1. Generate hash       │
         │  2. Check for duplicate │
         │  3. Quick score (0-100) │
         │  4. Insert to MongoDB   │
         │  5. If high match:      │
         │     → Telegram alert    │
         └─────────────────────────┘
```

## 2. Apply Pipeline Flow

```
User clicks "Apply"                Auto-apply scheduler
on dashboard                       picks up queued jobs
        │                                    │
        └──────────────┬─────────────────────┘
                       ▼
              ┌─────────────────┐
              │ ApplierManager  │
              │ .apply_to_job() │
              └────────┬────────┘
                       │
         ┌─────────────┼─────────────────┐
         ▼             ▼                 ▼
  ┌──────────┐  ┌──────────────┐  ┌──────────────┐
  │ Get Job  │  │ Get Base     │  │ Check:       │
  │ from DB  │  │ Resume       │  │ Already      │
  │          │  │ from DB      │  │ applied?     │
  └────┬─────┘  └──────┬───────┘  │ Score OK?    │
       │               │          └──────┬───────┘
       └───────┬───────┘                 │
               ▼                         │
  ┌─────────────────────────┐           │
  │  Claude AI: Tailor      │◄──────────┘
  │  Resume for this JD     │
  │  (preserve all facts,   │
  │   reword for relevance) │
  └───────────┬─────────────┘
              │
              ▼
  ┌─────────────────────────┐
  │  Claude AI: Generate    │
  │  Cover Letter           │
  │  (3-4 paragraphs,      │
  │   specific to company)  │
  └───────────┬─────────────┘
              │
              ▼
  ┌─────────────────────────┐
  │  PDF Generator:         │
  │  • Original-style PDF   │
  │  • Clean-template PDF   │
  │  • Cover letter PDF     │
  └───────────┬─────────────┘
              │
              ▼
  ┌─────────────────────────┐
  │  Portal-specific        │
  │  Applier (Playwright):  │
  │  • Navigate to job      │
  │  • Click Apply          │
  │  • Fill form fields     │
  │  • Upload resume        │
  │  • Submit               │
  └───────────┬─────────────┘
              │
       ┌──────┴──────┐
       ▼             ▼
  ┌─────────┐  ┌─────────┐
  │ SUCCESS │  │ FAILED  │
  └────┬────┘  └────┬────┘
       │            │
       ▼            ▼
  ┌─────────────────────────┐
  │  Create Application     │
  │  record in MongoDB      │
  │  with status + events   │
  └───────────┬─────────────┘
              │
              ▼
  ┌─────────────────────────┐
  │  Telegram notification  │
  │  (success or failure)   │
  └─────────────────────────┘
```

## 3. Resume Tailoring Flow

```
  ┌──────────────┐     ┌──────────────────┐
  │ Base Resume  │     │ Job Description  │
  │ (your real   │     │ (scraped from    │
  │  resume)     │     │  portal)         │
  └──────┬───────┘     └────────┬─────────┘
         │                      │
         └──────────┬───────────┘
                    ▼
         ┌──────────────────────┐
         │    Claude AI API     │
         │                      │
         │  System Prompt:      │
         │  "You are a resume   │
         │   expert. NEVER      │
         │   fabricate..."      │
         │                      │
         │  Input:              │
         │  • Full resume text  │
         │  • Full job desc     │
         │  • Required skills   │
         │  • Company name      │
         └──────────┬───────────┘
                    │
                    ▼
         ┌──────────────────────┐
         │  Structured JSON     │
         │  Response:           │
         │  • tailored summary  │
         │  • reordered skills  │
         │  • reworded bullets  │
         │  • changes log       │
         │  • ATS keywords      │
         └──────────┬───────────┘
                    │
           ┌───────┴───────┐
           ▼               ▼
  ┌─────────────┐  ┌─────────────┐
  │ Original    │  │ Clean       │
  │ Template    │  │ Template    │
  │ (LaTeX-like)│  │ (Modern)    │
  └──────┬──────┘  └──────┬──────┘
         │               │
         ▼               ▼
  ┌─────────────┐  ┌─────────────┐
  │ PDF via     │  │ PDF via     │
  │ WeasyPrint  │  │ WeasyPrint  │
  └─────────────┘  └─────────────┘
```

## 4. Job Match Scoring Flow

```
         ┌──────────────┐
         │  New Job      │
         │  Scraped      │
         └──────┬───────┘
                │
                ▼
  ┌──────────────────────────┐
  │  QUICK SCORE (no API)    │
  │  Heuristic-based:        │
  │  • Skills overlap (50pt) │
  │  • Location match (20pt) │
  │  • Title keywords (30pt) │
  │  = 0-100 rough score     │
  └──────────┬───────────────┘
             │
             │  Score saved to DB
             │
             ▼
  ┌──────────────────────────┐
  │  User clicks "Re-score"  │
  │  OR auto-score for       │
  │  high quick-score jobs   │
  └──────────┬───────────────┘
             │
             ▼
  ┌──────────────────────────┐
  │  FULL AI SCORE (Claude)  │
  │  Analyzes:               │
  │  • Skills (35%)          │
  │  • Experience fit (25%)  │
  │  • Role alignment (20%) │
  │  • Location (10%)        │
  │  • Growth potential (10%)│
  │  = 0-100 precise score   │
  │  + detailed reasoning    │
  └──────────────────────────┘
```

## 5. Notification Flow

```
  ┌──────────────────┐
  │ Event occurs:    │
  │ • High-match job │
  │ • App submitted  │
  │ • App failed     │
  │ • Scrape done    │
  │ • Daily summary  │
  └────────┬─────────┘
           │
           ▼
  ┌──────────────────┐    ┌──────────────────┐
  │ Dashboard        │    │ Telegram Bot     │
  │ (always updated  │    │ (if configured)  │
  │  via API polling)│    │                  │
  └──────────────────┘    └──────────────────┘
```
