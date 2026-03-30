"""
JOBPILOT — Job URL Parser

Extracts job details (title, company, location, description, skills)
from any job posting URL. Uses a 3-tier extraction strategy:

1. LD+JSON JobPosting schema (most ATS platforms: Ashby, Greenhouse, Lever, Workday)
2. OpenGraph / meta tags (LinkedIn, most career pages)
3. <title> tag parsing with platform-specific patterns
"""

import re
import json
import httpx
from bs4 import BeautifulSoup
from utils.logger import logger

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9",
}

# Platform-specific title patterns: regex → (title_group, company_group, location_group)
TITLE_PATTERNS = [
    # LinkedIn: "Company hiring Title in Location | LinkedIn"
    (r'^(.+?) hiring (.+?) in (.+?) \| LinkedIn$', 2, 1, 3),
    # Naukri: "Title Job in Location - Company | Naukri.com"
    (r'^(.+?) Job in (.+?) - (.+?) \| Naukri\.com$', 1, 3, 2),
    # Indeed: "Title - Company - Location | Indeed.com"
    (r'^(.+?) - (.+?) - (.+?) \| Indeed\.com$', 1, 2, 3),
    # Glassdoor: "Title at Company | Glassdoor"
    (r'^(.+?) at (.+?) \| Glassdoor$', 1, 2, None),
    # Greenhouse: "Title at Company"
    (r'^(.+?) at (.+?)$', 1, 2, None),
    # Generic: "Title - Company | Portal"
    (r'^(.+?) [-–—] (.+?) \|.+$', 1, 2, None),
    # Generic: "Title - Company"
    (r'^(.+?) [-–—] (.+?)$', 1, 2, None),
    # Generic: "Title @ Company"
    (r'^(.+?) @ (.+?)$', 1, 2, None),
]


def _extract_skills_from_text(text: str) -> list:
    """Extract common tech skills from description text."""
    if not text:
        return []
    known = [
        "Python", "Java", "JavaScript", "TypeScript", "Go", "Rust", "C++", "C#", "Ruby", "Kotlin", "Swift", "Scala",
        "React", "Angular", "Vue", "Node.js", "Express", "Django", "Flask", "FastAPI", "Spring Boot", "Rails",
        "AWS", "GCP", "Azure", "Docker", "Kubernetes", "Terraform", "CI/CD",
        "PostgreSQL", "MySQL", "MongoDB", "Redis", "DynamoDB", "Elasticsearch",
        "REST API", "GraphQL", "gRPC", "Microservices", "System Design",
        "Machine Learning", "Deep Learning", "NLP", "Computer Vision",
        "Git", "Linux", "Agile", "Scrum",
    ]
    text_lower = text.lower()
    return [s for s in known if s.lower() in text_lower]


async def fetch_job_details(url: str) -> dict:
    """
    Fetch and parse job details from any URL.
    Returns dict with: title, company, location, description, skills, job_type, source
    """
    result = {"url": url, "title": "", "company": "", "location": "", "description": "", "skills": [], "job_type": ""}

    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=15) as client:
            r = await client.get(url, headers=HEADERS)
        soup = BeautifulSoup(r.text, "lxml")
    except Exception as e:
        logger.warning(f"Failed to fetch {url}: {e}")
        result["error"] = f"Could not fetch URL: {str(e)[:100]}"
        return result

    # === Tier 1: LD+JSON JobPosting (most reliable) ===
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string)
            items = [data] if isinstance(data, dict) else data if isinstance(data, list) else []
            for item in items:
                if not isinstance(item, dict) or item.get("@type") != "JobPosting":
                    continue
                result["title"] = item.get("title", "")
                org = item.get("hiringOrganization", {})
                result["company"] = org.get("name", "") if isinstance(org, dict) else str(org)
                # Location
                loc = item.get("jobLocation")
                if isinstance(loc, list) and loc:
                    addr = loc[0].get("address", {}) if isinstance(loc[0], dict) else {}
                elif isinstance(loc, dict):
                    addr = loc.get("address", {})
                else:
                    addr = {}
                parts = [addr.get("addressLocality", ""), addr.get("addressRegion", ""), addr.get("addressCountry", "")]
                result["location"] = ", ".join(p for p in parts if p)
                # Description — strip HTML
                desc_html = item.get("description", "")
                result["description"] = BeautifulSoup(desc_html, "lxml").get_text(separator="\n").strip()[:5000] if desc_html else ""
                result["job_type"] = item.get("employmentType", "")
                result["skills"] = _extract_skills_from_text(result["description"])
                result["source"] = "structured"
                return result
        except Exception:
            pass

    # === Tier 2: OG tags ===
    og_title = soup.find("meta", property="og:title")
    og_desc = soup.find("meta", property="og:description")
    if og_title and og_title.get("content"):
        result["title"] = og_title["content"].strip()
    if og_desc and og_desc.get("content"):
        result["description"] = og_desc["content"].strip()[:5000]

    # === Tier 3: <title> tag with pattern matching ===
    raw_title = soup.title.string.strip() if soup.title and soup.title.string else ""
    if raw_title:
        # Try platform-specific patterns
        for pattern, t_grp, c_grp, l_grp in TITLE_PATTERNS:
            m = re.match(pattern, raw_title)
            if m:
                if not result["title"]:
                    result["title"] = m.group(t_grp).strip()
                if not result["company"]:
                    result["company"] = m.group(c_grp).strip()
                if l_grp and not result["location"]:
                    result["location"] = m.group(l_grp).strip()
                break
        # If no pattern matched, use raw title
        if not result["title"]:
            result["title"] = raw_title

    # === Tier 4: meta description fallback ===
    if not result["description"]:
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            result["description"] = meta_desc["content"].strip()[:5000]

    # Extract skills from whatever description we got
    if not result["skills"] and result["description"]:
        result["skills"] = _extract_skills_from_text(result["description"])

    result["source"] = "meta"
    return result
