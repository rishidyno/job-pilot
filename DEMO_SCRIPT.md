# JobPilot — Demo Video Script & LinkedIn Post

---

## LinkedIn Post

```
I was spending 3+ hours a day across 5 job portals.
Same searches. Same filters. Copy-pasting into a spreadsheet.

So I built a tool to do it for me — while actively job hunting myself.

Introducing JobPilot 🚀

Here's what it does:

🔍 Auto-scrapes LinkedIn & Indeed on a schedule
   No logins. No credentials. Just results, automatically.

🎯 Scores every job 0–100 against YOUR skills & roles
   Skill match highlighting shows exactly why a job fits (or doesn't)

📄 AI resume tailoring — one click per job
   Write your LaTeX resume once.
   Gemini rewrites a tailored copy for each job description.
   You control what the AI can and can't touch via editable rules.

📋 Kanban board for tracking every application
   Drag between: Pending → Applied → Interview → Offered → Rejected
   (There's confetti when you hit Offered 🎉)

📊 Dashboard with real data
   Jobs over time, per-portal breakdown, application pipeline,
   most in-demand skills across all your scraped jobs

⚙️ Everything configurable from the UI
   Target roles, locations, skills, scrape schedule — no .env editing needed

Bonus: job comparison side-by-side, CSV export, bookmarks,
add any job manually by pasting a URL, 6 UI themes, keyboard shortcuts

I wanted auto-apply too. Didn't ship it.
Turns out finding the RIGHT jobs first is the harder problem anyway.

Stack: FastAPI + React 18 + MongoDB + Google Gemini + python-jobspy
Self-hosted. Your data stays yours.

Repo in comments 👇

#buildinpublic #jobsearch #python #react #fastapi #gemini #opensource #sideproject
```

---

## Demo Video Script

**Target duration: 2 minutes**
**Format:** Screen recording with voiceover. Light background music at low volume throughout.
**Resolution:** 1080p, 60fps preferred.
**Theme to use:** Dark or Midnight (looks best on video).
**Browser zoom:** 90% so more UI fits on screen.

> **How to use this script:**
> Each shot has what to **show on screen** and exactly what to **say out loud**.
> Speak naturally — don't rush. The timings are guides, not hard limits.
> Record your voice separately and sync it in editing if needed.

---

### Shot 1 — The Problem (0:00–0:10)

**Show:** Open 4–5 browser tabs — LinkedIn Jobs, Indeed, Naukri, Glassdoor, a messy spreadsheet.
**Action:** Slowly tab between them.

**🎙 Say:**
> "If you've ever been job hunting, you know what this looks like.
> Five different portals, same searches every day, manually copy-pasting jobs into a spreadsheet.
> I got tired of it — so I built something to fix it."

---

### Shot 2 — Landing Page (0:10–0:18)

**Show:** The JobPilot landing page. Scroll slowly through it.

**🎙 Say:**
> "This is JobPilot — an AI-powered job hunting dashboard I built
> over the last two weeks, while actively looking for a job myself."

---

### Shot 3 — Onboarding & Dashboard (0:18–0:32)

**Show:** Log in → the 4-step onboarding modal appears (set target roles, locations, skills).
**Action:** Quickly fill in roles ("Software Engineer", "Backend Developer"), skills, location → complete onboarding.
**Transition:** Land on the Dashboard — 6 stats cards (Total Jobs, New Today, High Matches, Applied, Interviews, Avg Score), line chart, portal bar chart, application pipeline, activity feed.

**🎙 Say:**
> "When you first log in, a quick onboarding walks you through setting your target roles,
> locations, and skills. That's all the tool needs to get started.
> And this is your dashboard — total jobs found, high matches, applications, interviews,
> average match score — everything at a glance."

---

### Shot 4 — Live Scrape (0:32–0:52)

**Show:** Click "Scrape Jobs" → portal selector → select LinkedIn and Indeed → Start. Watch the live log terminal stream in real time. Show counters updating — Found, New, High Matches. Scrape completes, dashboard updates.

**🎙 Say:**
> "Hit Scrape Jobs, pick your portals, and watch it go.
> It scrapes LinkedIn and Indeed automatically — no logins, no API keys,
> just public data.
> You can see every step in real time — which keywords it's searching,
> which jobs it found, and which ones are a strong match for your profile.
> When it's done, the dashboard updates instantly."

---

### Shot 5 — Jobs Page (0:52–1:14)

**Show:**
- Navigate to Jobs page — cards with score badges
- Open a job card — skill match section highlighted
- Click AI Score button — loading → score + reasoning appears
- Apply filters — portal: LinkedIn, min score: 70, sort by Match Score
- Bookmark a job, filter by bookmarked
- Select 2 jobs → Compare → side-by-side modal
- Click "+ Add Job" → paste URL → auto-extracted details
- Click "↓ Export" → CSV downloads

**🎙 Say:**
> "Every scraped job gets a match score out of 100 — based on your skills, target roles,
> and location. You can see exactly which of your skills match the job requirements.
> Want a deeper AI score? One click — Gemini analyses the full job description
> and gives you a score with reasoning.
> You can filter by portal, minimum score, sort by relevance.
> Bookmark jobs to revisit later.
> Compare two jobs side by side if you're deciding between them.
> You can also add any job manually by just pasting a URL —
> the tool extracts all the details automatically.
> And you can export everything to CSV whenever you want."

---

### Shot 6 — AI Resume Tailoring (1:14–1:34)

**Show:**
- On a job card, click "Tailor Resume" → loading → success toast with updated score
- Navigate to Resume Manager
- Show base LaTeX in Monaco editor
- Click "Preview PDF" → PDF renders
- Show the tailored versions list → open the tailored copy → highlight changed sections

**🎙 Say:**
> "This is probably my favourite feature.
> You write your resume once in LaTeX — right here in this VS Code-style editor.
> Hit 'Tailor Resume' on any job, and Gemini rewrites a tailored copy
> specifically for that job description — highlighting the right skills,
> reordering bullet points, adjusting the summary.
> It compiles straight to PDF so you can preview it instantly.
> And you control exactly what the AI is allowed to change —
> through an editable rules file, so it never makes things up."

---

### Shot 7 — Application Tracking (1:34–1:48)

**Show:**
- Navigate to Applications → Kanban board
- Show columns: Pending → Applied → Interview → Offered → Rejected
- Drag a card from Applied → Interview
- Drag another to Offered → confetti
- Toggle to List view → expandable cards with timeline

**🎙 Say:**
> "Once you start applying, track everything on the Kanban board.
> Drag cards between stages as things progress.
> And when you get an offer —
> *(pause for confetti)*
> — yeah, there's confetti.
> If Kanban isn't your thing, switch to list view — you get a full timeline
> of every status change for each application."

---

### Shot 8 — Settings (1:48–1:56)

**Show:**
- Settings page → Profile section (roles, skills, locations, experience)
- Scheduler (scrape interval, next run time, portal status)
- AI Rules markdown editor with live preview
- Candidate Profile markdown editor

**🎙 Say:**
> "Everything is configurable from the UI — no touching config files.
> Set your target roles, skills, experience range, locations.
> Configure how often the scraper runs automatically in the background.
> And the AI rules and candidate profile are just markdown files
> you edit directly in the browser — this is what gets sent to Gemini
> every time it tailors your resume."

---

### Shot 9 — UI Polish & Closing (1:56–2:00)

**Show:** Quickly cycle themes — Dark → Midnight → Emerald → Nord. End back on dashboard.
**Final screen:** Static text card.

**🎙 Say:**
> "Oh — and there are six themes, because why not.
> The repo is open source, link's in the description.
> If you're also in the job market right now — good luck out there."

**Final on-screen text:**
```
JobPilot
Open Source  ·  Self-hosted  ·  MIT License
github.com/rishidyno/job-pilot
Built by Rishi Raj
```

---

## Recording Tips

- Use **OBS Studio** (free) or **ShareX** for screen recording.
- Set browser zoom to **90%** so more UI fits without scrolling.
- Use the **Midnight theme** — darkest background, most contrast on video.
- **Run a real scrape before recording** so the dashboard already has jobs and data. Empty charts look bad.
- The live scrape log (Shot 4) is your strongest shot — record it in real time, don't speed it up.
- Record voiceover in a quiet room. Phone mic is fine if you speak close to it.
- Keep music at 10–15% volume — just enough to fill silence, not compete with your voice.
- Edit in **DaVinci Resolve** (free) or **CapCut** — trim dead air between actions, sync voice to screen.
