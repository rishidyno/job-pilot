"""
╔═══════════════════════════════════════════════════════════════════╗
║  JOBPILOT — Helper Utilities                                     ║
║                                                                   ║
║  Shared utility functions used across multiple modules.           ║
║  Keep these stateless and pure where possible.                    ║
╚═══════════════════════════════════════════════════════════════════╝
"""

import re
import hashlib
import asyncio
import random
from datetime import datetime, timezone
from typing import Optional
from bson import ObjectId
from fastapi import HTTPException


def valid_oid(id_str: str) -> ObjectId:
    """Validate and convert string to ObjectId. Raises 400 on invalid."""
    try:
        return ObjectId(id_str)
    except Exception:
        raise HTTPException(status_code=400, detail=f"Invalid ID format: {id_str}")


def utc_now() -> datetime:
    """
    Get the current UTC timestamp.
    
    Always use this instead of datetime.now() to ensure
    consistent timezone handling across the app.
    
    Returns:
        datetime: Current time in UTC
    """
    return datetime.now(timezone.utc)


def generate_job_hash(portal: str, external_id: str) -> str:
    """
    Generate a unique hash for a job listing.
    
    Used for deduplication — if the same job appears on multiple
    scrape runs, we use this hash to detect it's the same job.
    
    Args:
        portal: Job portal name (e.g., "linkedin", "naukri")
        external_id: The portal's unique ID for this job
    
    Returns:
        str: SHA-256 hash of portal + external_id
    
    Example:
        hash = generate_job_hash("linkedin", "3847291056")
        # => "a3f7c2..."
    """
    raw = f"{portal}:{external_id}"
    return hashlib.sha256(raw.encode()).hexdigest()


def clean_text(text: str) -> str:
    """
    Clean scraped text by removing extra whitespace, newlines, etc.
    
    Scraped HTML often has messy whitespace. This normalizes it
    to clean, single-spaced text suitable for AI processing.
    
    Args:
        text: Raw scraped text
    
    Returns:
        str: Cleaned text with normalized whitespace
    """
    if not text:
        return ""
    # Replace multiple whitespace/newlines with single space
    text = re.sub(r'\s+', ' ', text)
    # Strip leading/trailing whitespace
    text = text.strip()
    return text


def truncate_text(text: str, max_length: int = 5000) -> str:
    """
    Truncate text to a maximum length, adding ellipsis if truncated.
    
    Used when sending job descriptions to Claude API to avoid
    exceeding token limits.
    
    Args:
        text: Text to truncate
        max_length: Maximum allowed character length
    
    Returns:
        str: Truncated text (with "..." if cut)
    """
    if not text or len(text) <= max_length:
        return text or ""
    return text[:max_length - 3] + "..."


def parse_experience_years(text: str) -> Optional[float]:
    """
    Extract years of experience from a job posting's experience requirement.
    
    Job portals express experience in many formats:
    - "1-3 years"
    - "2+ years experience"
    - "1.5 to 3 yrs"
    - "Entry level (0-2 years)"
    
    This function extracts the minimum years mentioned.
    
    Args:
        text: Raw experience text from job posting
    
    Returns:
        float or None: Minimum years of experience, or None if unparseable
    
    Examples:
        parse_experience_years("1-3 years")  # => 1.0
        parse_experience_years("2+ years")   # => 2.0
        parse_experience_years("fresher")    # => 0.0
    """
    if not text:
        return None

    text = text.lower().strip()

    # Handle "fresher" / "entry level" / "0 years"
    if any(word in text for word in ["fresher", "entry level", "entry-level", "0 year"]):
        return 0.0

    # Try to find patterns like "1-3", "1 to 3", "1.5-2.5", "2+"
    # This regex matches: number (optional decimal), optional dash/to, optional second number
    pattern = r'(\d+\.?\d*)\s*(?:[-–to]+\s*(\d+\.?\d*))?\s*(?:years?|yrs?|yr)'
    match = re.search(pattern, text)

    if match:
        return float(match.group(1))

    # Fallback: just find any number
    numbers = re.findall(r'\d+\.?\d*', text)
    if numbers:
        return float(numbers[0])

    return None


def format_salary(amount: Optional[float], currency: str = "INR") -> str:
    """
    Format a salary amount into a human-readable string.
    
    Args:
        amount: Salary amount (None if not available)
        currency: Currency code (default: INR)
    
    Returns:
        str: Formatted salary string
    
    Examples:
        format_salary(1500000)        # => "₹15.0L"
        format_salary(None)           # => "Not disclosed"
        format_salary(150000, "USD")  # => "$150,000"
    """
    if amount is None:
        return "Not disclosed"

    if currency == "INR":
        if amount >= 10000000:  # 1 Crore+
            return f"₹{amount / 10000000:.1f}Cr"
        elif amount >= 100000:  # 1 Lakh+
            return f"₹{amount / 100000:.1f}L"
        else:
            return f"₹{amount:,.0f}"
    elif currency == "USD":
        return f"${amount:,.0f}"
    else:
        return f"{currency} {amount:,.0f}"


def to_object_id(id_str: str) -> ObjectId:
    """
    Safely convert a string to MongoDB ObjectId.
    
    Args:
        id_str: String representation of ObjectId
    
    Returns:
        ObjectId: MongoDB ObjectId
    
    Raises:
        ValueError: If the string is not a valid ObjectId
    """
    try:
        return ObjectId(id_str)
    except Exception:
        raise ValueError(f"Invalid ObjectId: {id_str}")


async def random_delay(min_seconds: int = 2, max_seconds: int = 5) -> None:
    """
    Async sleep for a random duration within the given range.
    
    Used between scraping actions to appear more human-like
    and avoid rate limiting / bot detection.
    
    Args:
        min_seconds: Minimum delay (inclusive)
        max_seconds: Maximum delay (inclusive)
    """
    delay = random.uniform(min_seconds, max_seconds)
    await asyncio.sleep(delay)


def clean_url(url: str) -> str:
    """Clean a URL: keep essential query params, strip only tracking noise."""
    if not url:
        return ""
    from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

    parsed = urlparse(url)

    # For redirect URLs (e.g. indeed.com/rc/clk?jk=...) the query IS the link — keep it
    if not parsed.path or parsed.path in ('/', '/rc/clk', '/pagead/clk'):
        # Keep all params except known tracking ones
        tracking = {'bb', 'fccid', 'vjs', 'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content'}
        params = {k: v[0] for k, v in parse_qs(parsed.query).items() if k not in tracking}
        qs = urlencode(params) if params else parsed.query
        return urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', qs, ''))

    # For normal URLs, strip only tracking params but keep meaningful ones
    tracking = {'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'ref', 'fbclid', 'gclid'}
    if parsed.query:
        params = {k: v[0] for k, v in parse_qs(parsed.query).items() if k not in tracking}
        qs = urlencode(params) if params else ''
    else:
        qs = ''
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', qs, ''))


def extract_domain(url: str) -> str:
    """
    Extract the domain from a URL.
    
    Args:
        url: Full URL string
    
    Returns:
        str: Domain portion of the URL
    
    Example:
        extract_domain("https://www.linkedin.com/jobs/123")  # => "linkedin.com"
    """
    # Remove protocol
    domain = re.sub(r'^https?://', '', url)
    # Remove www.
    domain = re.sub(r'^www\.', '', domain)
    # Remove path
    domain = domain.split('/')[0]
    return domain


def sanitize_filename(name: str) -> str:
    """
    Convert a string into a safe filename.
    
    Removes special characters, replaces spaces with underscores,
    and truncates to 100 characters.
    
    Args:
        name: Raw string (e.g., job title or company name)
    
    Returns:
        str: Filesystem-safe filename
    
    Example:
        sanitize_filename("SDE-2 @ Google (Backend)")  # => "SDE-2_Google_Backend"
    """
    # Remove special characters except hyphens and underscores
    name = re.sub(r'[^\w\s-]', '', name)
    # Replace whitespace with underscores
    name = re.sub(r'\s+', '_', name)
    # Truncate to 100 chars
    return name[:100]
