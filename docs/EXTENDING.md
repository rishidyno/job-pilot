# JobPilot — Extension Guide

## How to Extend JobPilot

JobPilot is designed with a modular, plugin-like architecture. Here's how to extend each part.

---

## 1. Add a New Job Portal (Scraper + Applier)

**Time: ~30 minutes per portal**

See [SCRAPER_GUIDE.md](./SCRAPER_GUIDE.md) for detailed instructions.

Quick summary:
1. Create `backend/scrapers/myportal_scraper.py` → extend `BaseScraper`
2. Create `backend/appliers/myportal_applier.py` → extend `BaseApplier`
3. Register both in their respective `*_manager.py` files
4. Add credentials to `config.py` and `.env.example`

---

## 2. Add a New AI Provider

Currently uses Claude (Anthropic). To add OpenAI, Gemini, or a local LLM:

1. Create `backend/services/openai_service.py` (or similar)
2. Implement the same interface as `ai_service.py`:
   - `async chat(user_message, system_prompt, ...) → dict`
   - `async chat_json(user_message, system_prompt, ...) → dict`
3. Update `config.py` with a new `AI_PROVIDER` setting
4. In the services that use AI (`resume_tailor.py`, `cover_letter_service.py`, `job_matcher.py`), import based on the config:
   ```python
   if settings.AI_PROVIDER == "openai":
       from services.openai_service import ai_service
   else:
       from services.ai_service import ai_service
   ```

---

## 3. Add a New Notification Channel

Currently supports Dashboard + Telegram. To add Slack, Email, Discord:

1. Create `backend/services/slack_service.py`
2. Implement the same notification methods as `telegram_service.py`:
   - `notify_new_job(...)`
   - `notify_application_submitted(...)`
   - `notify_application_failed(...)`
   - `notify_scrape_complete(...)`
   - `notify_daily_summary(...)`
3. Create a `notification_manager.py` that fans out to all enabled channels
4. Update `config.py` with channel-specific settings

---

## 4. Add New Resume Templates

1. Create a new HTML template in `backend/templates/`:
   - e.g., `resume_creative.html` or `resume_ats.html`
2. Use Jinja2 template variables: `{{ name }}`, `{{ summary }}`, `{{ experience }}`, etc.
3. Update `pdf_generator.py` to support the new template:
   ```python
   template_file = {
       "original": "resume_original.html",
       "clean": "resume_clean.html",
       "creative": "resume_creative.html",  # ← new
   }.get(template_style)
   ```
4. Update the frontend to show the new option

---

## 5. Add New Dashboard Pages

1. Create a new page component in `frontend/src/pages/MyPage.jsx`
2. Add a route in `frontend/src/App.jsx`:
   ```jsx
   <Route path="/mypage" element={<MyPage />} />
   ```
3. Add a nav item in `frontend/src/components/Sidebar.jsx`
4. Create any new API endpoints needed in `backend/routers/`

---

## 6. Add Authentication (if exposing publicly)

Currently JobPilot has NO authentication (designed for localhost use). To add auth:

1. Install `python-jose[cryptography]` and `passlib[bcrypt]`
2. Create `backend/auth/` with JWT token generation
3. Add `Depends(get_current_user)` to all router endpoints
4. Add login page to the frontend
5. Store JWT in localStorage and attach to Axios headers

---

## 7. Add New Job Filters

To add filters like salary range, company size, etc.:

### Backend:
1. Add fields to `backend/models/job.py` (`JobCreate` and `Job`)
2. Update the scraper to extract the new data
3. Add query parameters in `backend/routers/jobs.py`

### Frontend:
1. Add filter inputs in `frontend/src/pages/Jobs.jsx`
2. Pass new params through the API client

---

## 8. Project Structure Conventions

When extending, follow these conventions:

- **Backend services** are singletons (module-level instance)
- **Models** use Pydantic v2 with `model_dump()` / `model_validate()`
- **Routers** are thin — delegate to services for logic
- **All async** — use `await` everywhere, Motor for MongoDB
- **Logging** — use `from utils.logger import logger` everywhere
- **Config** — all settings in `config.py`, read from `.env`
- **Comments** — docstrings on all classes/methods, inline comments for non-obvious logic
