# JobPilot — Scraper Guide

## Overview

JobPilot uses [python-jobspy](https://github.com/speedyapply/JobSpy) as its scraping engine. No login credentials or browser automation needed — it uses public/guest APIs from each portal.

## Supported Portals

| Portal | Method | Notes |
|--------|--------|-------|
| LinkedIn | Guest API (`/jobs-guest/`) | No login, rate limits after ~100 results |
| Indeed | Public search pages | Best scraper, no rate limiting |
| Glassdoor | Public search | Reviews + salary data |
| Google Jobs | Search aggregation | Aggregated from multiple sources |
| Naukri | Public API | India-focused, includes skills + experience |

## How It Works

```
User clicks "Scrape Now"
    ↓
scraper_manager.py reads user preferences from MongoDB
    ↓
Keyword expansion: "Backend Engineer" → also "Java Developer", "SDE", etc.
    ↓
For each portal × keyword:
    python-jobspy scrape_jobs() runs in asyncio.to_thread()
    ↓
    Results (DataFrame) → process each job:
        - Generate dedup hash
        - Quick match score (skills overlap + location + title)
        - Insert to MongoDB (skip duplicates)
        - Telegram notification if high match
    ↓
Live events emitted to frontend via polling
```

## Configuration

All scraping preferences are user-controlled from the Settings page:

- **Target roles** → keywords to search
- **Target locations** → location parameter
- **Primary skills** → used for match scoring
- **Experience range** → filters results
- **Min match score** → threshold for "high match" notifications
- **Scrape interval** → how often the scheduler runs

## Keyword Expansion

The scraper automatically generates search variations:

```python
"Backend Engineer" → ["Backend Engineer", "Software Engineer Backend", "Java Developer", "Server Side Engineer"]
"Full Stack Developer" → ["Full Stack Developer", "Fullstack Developer", "Full Stack Engineer"]
"SDE-1" → ["SDE-1", "SDE 1", "Software Development Engineer"]
```

This dramatically increases coverage — a single target role generates 2-4 search queries.

## Adding a New Portal

If python-jobspy adds support for a new portal:

1. Add the portal name to `SUPPORTED_PORTALS` in `scraper_manager.py`
2. Add it to the frontend `ScrapeModal.jsx` portal list
3. Add portal color to `Dashboard.jsx` and `helpers.js`

If you need a custom scraper (not supported by jobspy):

1. Create a function that returns a list of job dicts
2. Call it from `_scrape_portal()` in `scraper_manager.py`
3. The processing pipeline (dedup, scoring, DB insert) is shared

## Rate Limits

| Portal | Limit | Mitigation |
|--------|-------|------------|
| LinkedIn | ~100 results per IP | Use proxies for higher volume |
| Indeed | No significant limits | Best for bulk scraping |
| Glassdoor | Moderate | 1s delay between requests |
| Google | Moderate | Specific query syntax required |
| Naukri | Moderate | Standard rate limiting |

python-jobspy handles delays internally. For higher volume, pass proxies:

```python
scrape_jobs(proxies=["user:pass@host:port"])
```
