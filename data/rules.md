# AI Resume Tailoring Rules
# Author: Rishi Raj
# Last Updated: March 2026
# Purpose: Rules for auto-tailoring resume based on JD input

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
if jd contains [Python, Flask, FastAPI, Django, ML, TensorFlow, PyTorch, AI]:
  language_order: [Python, Java, C/C++, JavaScript, Kotlin]
  job_title_tech: "Python, AWS, Distributed Systems, Microservices"

if jd contains [Java, Spring Boot, Spring, JVM, J2EE, Hibernate]:
  language_order: [Java, Python, C/C++, JavaScript, Kotlin]
  job_title_tech: "Java, Spring Boot, AWS, Microservices"

if jd contains [Go, Golang]:
  language_order: [Java, Python, C/C++, JavaScript, Kotlin]
  add_note: "— open to Go"
  job_title_tech: "Java, Python, Distributed Systems, Microservices"

if jd contains [Node, NodeJS, JavaScript, TypeScript]:
  language_order: [JavaScript, Java, Python, C/C++, Kotlin]
  job_title_tech: "Node.js, JavaScript, REST APIs, Microservices"

if no clear primary language detected:
  use: primary_java (default)
```

---

## RULE 2 — SUMMARY SELECTION

### rule: summary_selector
Pick the correct summary variant from profile.md based on JD signals.

```yaml
if company_type == startup AND jd contains [AI, ML, agentic, LLM, detection]:
  use: summary_ai_startup

if company_type == enterprise AND jd contains [Java, Spring Boot, SDLC, Kafka, SQL]:
  use: summary_enterprise_java

if jd contains [Python, ML, TensorFlow, anomaly, data pipeline, Spark]:
  use: summary_python_ml

default:
  use: summary_general
```

---

## RULE 3 — COMPANY TYPE DETECTION

### rule: company_type_classifier
Classify company type to apply the right tone and emphasis.

```yaml
signals_startup:
  - team_size < 50
  - keywords: [founding engineer, early team, fast-paced, ownership, YC, seed, Series A/B]
  - tone: ownership-driven, bias for action

signals_enterprise:
  - keywords: [SDLC, agile, compliance, process, Fortune 500, enterprise]
  - companies: [Amazon, Google, Microsoft, Optum, UHG, Oracle, IBM, Infosys, TCS]
  - tone: process-oriented, reliability, quality

signals_product_startup:
  - keywords: [product engineer, full ownership, ship fast, iterate]
  - tone: end-to-end ownership, shipping mindset

signals_security_company:
  - keywords: [DLP, data protection, PII, PHI, sensitive data, compliance, SIEM, SOAR]
  - emphasis: agentic_ai, anomaly_detection, data_classification

signals_gaming_consumer:
  - keywords: [live streaming, gaming, real-time, WebSocket, Firebase, latency]
  - emphasis: low_latency, fault_tolerant, concurrent

signals_fintech:
  - keywords: [banking, NBFC, lending, payment, transaction, reconciliation]
  - emphasis: colending, rule_engine, financial_integrity
```

---

## RULE 4 — BULLET PRIORITY & SELECTION

### rule: bullet_ordering
Always-include bullets (core, never remove):

```yaml
always_include:
  - bullet_stuck_transaction      # $5M impact — universal signal of ownership
  - bullet_project_montana        # end-to-end ownership signal
  - bullet_agentic_ai             # AI differentiator — rare for SDE-1
  - bullet_search_service         # clean, universal backend signal
```

### rule: bullet_selector_by_role

```yaml
if role_type == backend_distributed:
  prioritize:
    - bullet_agentic_ai
    - bullet_project_montana
    - bullet_ark_framework
    - bullet_stuck_transaction
    - bullet_marketplace_logic
    - bullet_india_launch
    - bullet_search_service
    - bullet_colending

if role_type == java_enterprise:
  prioritize:
    - bullet_project_montana
    - bullet_ark_framework
    - bullet_stuck_transaction
    - bullet_marketplace_logic
    - bullet_search_service
    - bullet_colending
    - bullet_rule_engine
    - bullet_india_launch
  bullet_rule_engine_note: "reframe as: Drools-based Rule Engine aligns with policy/workflow engines"

if role_type == ai_ml_backend:
  prioritize:
    - bullet_agentic_ai           # MUST be bullet #1
    - bullet_project_montana
    - bullet_india_launch
    - bullet_stuck_transaction
    - bullet_marketplace_logic
    - bullet_search_service
  bullet_agentic_ai_reframe: "Lead with Python + anomaly detection + autonomous systems language"

if role_type == startup_founding:
  prioritize:
    - bullet_agentic_ai
    - bullet_project_montana
    - bullet_ark_framework
    - bullet_stuck_transaction
    - bullet_marketplace_logic
    - bullet_india_launch
  tone: "Emphasize ownership, end-to-end, founding-team energy"

if role_type == security_dlp:
  prioritize:
    - bullet_agentic_ai           # reframe as autonomous detection & response
    - bullet_project_montana
    - bullet_stuck_transaction
    - bullet_marketplace_logic
    - bullet_rule_engine          # reframe as detection rule engine
    - bullet_healthcare_data      # sensitive data handling
  bullet_agentic_ai_reframe: "Compare to autonomous DLP analyst / detection system"
  bullet_rule_engine_reframe: "Pattern closely aligned with detection rule engines in security platforms"
```

---

## RULE 5 — SKILLS SECTION TAILORING

### rule: skills_builder

```yaml
always_include_skills:
  - languages (reordered per Rule 1)
  - backend_frameworks.core
  - databases.relational + databases.nosql
  - cloud_devops.core
  - core_cs.core

add_if_jd_mentions:
  kafka:              messaging_streaming.core
  spark / hadoop:     messaging_streaming.exposure (label as "exposure")
  redis:              databases.nosql
  cassandra:          databases.nosql (label as "exposure")
  kubernetes / k8s:   cloud_devops.exposure (label as "learning")
  terraform:          cloud_devops.exposure (label as "exposure")
  jenkins / sonar:    cloud_devops.exposure
  graphql:            backend_frameworks.additional
  flask:              backend_frameworks.additional
  tensorflow:         ai_ml.exposure (label as "exposure")
  solr:               messaging_streaming.exposure (label as "exposure")
  mysql:              databases.relational
  redshift:           databases.cloud_db (label as "exposure")
  go / golang:        append "— open to Go" to languages

never_claim_without_basis:
  - Kubernetes (only say "learning" or "exposure")
  - TensorFlow (only "exposure")
  - Terraform (only "exposure")
  - Spark (only "exposure")
```

---

## RULE 6 — ACHIEVEMENTS SELECTION

### rule: achievements_selector

```yaml
always_include:
  - codeforces       # DSA signal — always relevant
  - leetcode         # DSA signal — always relevant

include_if_relevant:
  - hackathon        # include if JD mentions Android, mobile, or hackathon culture
  - opensource       # include if JD mentions open-source, community, or testing

reframe_for_dsa_heavy_roles:
  codeforces: "Rated Specialist on Codeforces (max rating 1532) — strong DSA and algorithmic problem-solving"
  leetcode: "Solved 600+ DSA problems on LeetCode; consistent competitive programmer"
```

---

## RULE 7 — OPPIA / INTERNSHIP SECTION RULES

### rule: junior_experience_handling

```yaml
always_include_mfine: true
always_include_oppia: true

mfine_reframe_for_security: 
  add: "healthcare user data" context to bullet_healthcare_data

oppia_condense_if_space_tight:
  keep: [bullet_bazel, bullet_prs]
  drop: [bullet_uiux]

oppia_expand_if_space:
  keep_all: true
```

---

## RULE 8 — TONE & FRAMING RULES

### rule: tone_by_company_type

```yaml
startup_tone:
  - Use ownership language: "owned end-to-end", "drove", "spearheaded"
  - Mention: "production", "from design to deployment", "bias for action"
  - Avoid: corporate process words like "collaborated with stakeholders"

enterprise_tone:
  - Use process language: "within SDLC", "across teams", "following best practices"
  - Mention: "reliability", "fault tolerance", "SLAs", "scalability"
  - Include: CI/CD, testing, code quality mentions

ai_startup_tone:
  - Lead with AI/ML work
  - Use: "agentic", "autonomous", "anomaly detection", "production ML"
  - Draw analogy to their product if known
```

---

## RULE 9 — WHAT NEVER TO CHANGE

### rule: protected_content

```yaml
never_change:
  - Name: Rishi Raj
  - Phone: +91-8210239176
  - LinkedIn: https://www.linkedin.com/in/rishidyno/
  - GitHub: https://github.com/rishidyno/
  - CGPA: 8.24/10.00
  - Degree: B.Tech in Information Technology
  - Company names and dates

never_fabricate:
  - Do not claim Kubernetes expertise (only "learning")
  - Do not claim TensorFlow production experience (only "exposure")
  - Do not claim Go/Golang (only "open to")
  - Do not claim Spark production experience (only "exposure")
  - Do not invent new bullet points not grounded in actual work
  - Do not change metrics ($5M, 75%, 10x, 30+, 12+, 600+, 1532, 8.24)
```

---

## RULE 10 — RESUME FORMAT RULES

### rule: format_output

```yaml
output_formats:
  - pdf (default, via LaTeX compile)
  - docx (via docx-js)
  - latex (.tex source)

naming_convention: "{Company_Name}.pdf"
save_location: "Resume_Applications/"

page_limit: 1
font: Arial
font_size_body: 9.5pt
font_size_section_heading: 10pt
margins:
  top: 0.4in
  bottom: 0.5in
  left: 0.7in
  right: 0.75in

section_order:
  - Experience
  - Education
  - Achievements
  - Programming Skills

email_default: rishiraj727909@gmail.com
```

---

## RULE 11 — JD PARSING SIGNALS (QUICK REFERENCE)

### rule: jd_signal_map

```yaml
signal_keywords:
  java_role:          [Java, Spring Boot, JVM, Hibernate, J2EE, JUnit, Maven, Gradle]
  python_role:        [Python, Flask, FastAPI, Django, PyTorch, TensorFlow, NumPy, Pandas]
  distributed:        [distributed systems, microservices, Kafka, Redis, Cassandra, Zookeeper]
  ai_ml:              [ML, machine learning, AI, LLM, agentic, anomaly detection, model, inference]
  cloud_infra:        [AWS, GCP, Azure, Kubernetes, Docker, Terraform, CI/CD, DevOps]
  security:           [DLP, PII, PHI, sensitive data, data protection, SIEM, compliance, encryption]
  fintech:            [banking, NBFC, lending, payment, transaction, financial, reconciliation]
  gaming_realtime:    [gaming, live streaming, WebSocket, Firebase, real-time, low-latency]
  dsa_heavy:          [DSA, algorithms, data structures, competitive programming, problem solving]
  startup:            [founding, early team, fast-paced, ownership, YC, seed, startup]
  enterprise:         [SDLC, agile, Fortune 500, compliance, SLA, process, documentation]
```

---

## RULE 12 — LINKEDIN COLD MESSAGE RULES

### rule: cold_message_template

```yaml
message_format:
  opening: "Hi [Name], hope you're doing well!"
  intro: "I'm Rishi — SDE-1 at Amazon with ~1.8 years of backend experience (Java, Python, distributed systems)."
  ask: "I came across the [Role] role at [Company] and wanted to check if you'd be open to referring me."
  links:
    job: "Job link: [URL]"
    resume: "Resume: [Google Drive Link]"
  closing: "No pressure at all — really appreciate your time!\nRishi"

always_include:
  - Current role (SDE-1 at Amazon)
  - Job ID if available
  - Resume link
  - Job link

keep_short: true
max_lines: 10
```