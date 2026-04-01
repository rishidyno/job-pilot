# AI Resume Tailoring Rules
# Purpose: Rules for auto-tailoring resume based on JD input
# Edit this to customize how AI tailors your resume.

---

## HOW TO USE

1. Parse the incoming JD for signals (keywords, company type, role type, tech stack)
2. Match signals against rules below
3. Apply transformations to profile.md data
4. Output tailored resume

---

## RULE 1 — LANGUAGE PRIORITY

### rule: primary_language
Detect the primary language from JD and reorder accordingly.

```yaml
if jd contains [Python, Flask, FastAPI, Django, ML, TensorFlow]:
  language_order: [Python, <your other languages>]

if jd contains [Java, Spring Boot, Spring, JVM, Hibernate]:
  language_order: [Java, <your other languages>]

if jd contains [Node, NodeJS, JavaScript, TypeScript]:
  language_order: [JavaScript, <your other languages>]

if no clear primary language detected:
  use: <your default language order>
```

---

## RULE 2 — SUMMARY SELECTION

### rule: summary_selector
Pick the correct summary variant based on JD signals.

```yaml
if company_type == startup:
  use: summary_startup

if company_type == enterprise:
  use: summary_enterprise

default:
  use: summary_general
```

---

## RULE 3 — BULLET PRIORITY & SELECTION

### rule: bullet_ordering
Define which experience bullets are always included vs conditional.

```yaml
always_include:
  - <your strongest bullet — e.g. biggest impact metric>
  - <your most relevant technical bullet>

prioritize_by_role:
  backend: [<backend-relevant bullets>]
  frontend: [<frontend-relevant bullets>]
  fullstack: [<mix of both>]
```

---

## RULE 4 — SKILLS SECTION TAILORING

### rule: skills_builder

```yaml
always_include_skills:
  - languages (reordered per Rule 1)
  - core frameworks
  - databases
  - cloud/devops

add_if_jd_mentions:
  kafka: messaging/streaming
  kubernetes: cloud (label as "learning" if not proficient)
  terraform: cloud (label as "exposure" if not proficient)

never_claim_without_basis:
  - Do not claim expertise you don't have
  - Use "learning" or "exposure" labels for partial skills
```

---

## RULE 5 — WHAT NEVER TO CHANGE

### rule: protected_content

```yaml
never_change:
  - Your name and contact info
  - CGPA and degree
  - Company names and dates
  - Actual metrics and numbers

never_fabricate:
  - Do not invent experience or projects
  - Do not claim skills you don't have
  - Do not change real metrics
```

---

## RULE 6 — RESUME FORMAT RULES

### rule: format_output

```yaml
page_limit: 1
section_order:
  - Experience
  - Education
  - Achievements
  - Programming Skills
```
