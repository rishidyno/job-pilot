"""
╔═══════════════════════════════════════════════════════════════════╗
║  JOBPILOT — Configuration Management                             ║
║                                                                   ║
║  All app configuration lives here. Values are loaded from         ║
║  environment variables (via .env file) with sensible defaults.    ║
║                                                                   ║
║  HOW IT WORKS:                                                    ║
║  1. Pydantic Settings reads from .env file automatically          ║
║  2. Each setting has a type, default, and description             ║
║  3. Import `settings` anywhere: from config import settings       ║
║  4. Access values: settings.ANTHROPIC_API_KEY                     ║
║                                                                   ║
║  TO ADD A NEW SETTING:                                            ║
║  1. Add the field to the Settings class below                     ║
║  2. Add it to .env.example with documentation                     ║
║  3. Use it via `settings.YOUR_NEW_SETTING`                        ║
╚═══════════════════════════════════════════════════════════════════╝
"""

import os
from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Pydantic Settings automatically:
    - Reads from .env file
    - Validates types
    - Provides defaults
    - Raises errors for missing required fields
    """

    # ─────────────────────────────────────
    # REQUIRED — App won't start without these
    # ─────────────────────────────────────

    # Anthropic API key for Claude (optional — kiro-cli is used as AI engine by default)
    ANTHROPIC_API_KEY: str = ""

    # MongoDB connection string (e.g., mongodb://localhost:27017)
    MONGODB_URI: str = "mongodb://localhost:27017"

    # MongoDB database name
    MONGODB_DB_NAME: str = "jobpilot"

    # ─────────────────────────────────────
    # JOB SEARCH PREFERENCES
    # These define what jobs to look for
    # ─────────────────────────────────────

    # Comma-separated list of target job titles to search for
    TARGET_ROLES: str = "Software Engineer"

    # Minimum years of experience to target
    TARGET_EXPERIENCE_MIN: float = 0

    # Maximum years of experience to target
    TARGET_EXPERIENCE_MAX: float = 5

    # Comma-separated list of target locations
    TARGET_LOCATIONS: str = "Remote"

    # Comma-separated list of priority skills for job matching
    TARGET_SKILLS: str = ""

    # ─────────────────────────────────────
    # TELEGRAM NOTIFICATIONS
    # ─────────────────────────────────────

    # Telegram bot token (from @BotFather)
    TELEGRAM_BOT_TOKEN: str = ""

    # Your Telegram chat ID
    TELEGRAM_CHAT_ID: str = ""

    # ─────────────────────────────────────
    # JOB PORTAL CREDENTIALS
    # Only fill in portals you want to use
    # ─────────────────────────────────────

    LINKEDIN_EMAIL: str = ""
    LINKEDIN_PASSWORD: str = ""

    NAUKRI_EMAIL: str = ""
    NAUKRI_PASSWORD: str = ""

    WELLFOUND_EMAIL: str = ""
    WELLFOUND_PASSWORD: str = ""

    INSTAHYRE_EMAIL: str = ""
    INSTAHYRE_PASSWORD: str = ""

    INDEED_EMAIL: str = ""
    INDEED_PASSWORD: str = ""

    GLASSDOOR_EMAIL: str = ""
    GLASSDOOR_PASSWORD: str = ""

    # ─────────────────────────────────────
    # SCHEDULER SETTINGS
    # Controls when and how jobs are scraped/applied
    # ─────────────────────────────────────

    # How often to scrape job portals (in hours)
    SCRAPE_INTERVAL_HOURS: int = 6

    # Master switch: enable/disable auto-apply globally
    AUTO_APPLY_ENABLED: bool = False

    # Default mode: "auto" (no human review) or "semi" (review before apply)
    AUTO_APPLY_MODE: str = "semi"

    # Minimum match score (0-100) required to auto-apply to a job
    MIN_MATCH_SCORE_TO_APPLY: int = 70

    # ─────────────────────────────────────
    # AUTH / JWT
    # ─────────────────────────────────────

    # Secret key for signing JWT tokens (change in production!)
    JWT_SECRET_KEY: str = "jobpilot-super-secret-change-me-in-production"

    # JWT algorithm
    JWT_ALGORITHM: str = "HS256"

    # Token expiry in hours
    JWT_EXPIRY_HOURS: int = 72

    # ─────────────────────────────────────
    # ADVANCED / DEVELOPMENT
    # ─────────────────────────────────────

    # Logging level: DEBUG, INFO, WARNING, ERROR
    LOG_LEVEL: str = "INFO"

    # Playwright headless mode (set to false to see browser during scraping)
    PLAYWRIGHT_HEADLESS: bool = True

    # Backend server host
    BACKEND_HOST: str = "0.0.0.0"

    # Backend server port
    BACKEND_PORT: int = 8000

    # Frontend URL (for CORS configuration)
    FRONTEND_URL: str = "http://localhost:5173"

    # Rate limiting: random delay range (seconds) between scraping actions
    # This helps avoid detection by job portals
    SCRAPE_DELAY_MIN: int = 2
    SCRAPE_DELAY_MAX: int = 5

    # ─────────────────────────────────────
    # COMPUTED PROPERTIES
    # Derived from the settings above
    # ─────────────────────────────────────

    @property
    def target_roles_list(self) -> List[str]:
        """Parse comma-separated roles into a list."""
        return [role.strip() for role in self.TARGET_ROLES.split(",") if role.strip()]

    @property
    def target_locations_list(self) -> List[str]:
        """Parse comma-separated locations into a list."""
        return [loc.strip() for loc in self.TARGET_LOCATIONS.split(",") if loc.strip()]

    @property
    def target_skills_list(self) -> List[str]:
        """Parse comma-separated skills into a list."""
        return [skill.strip() for skill in self.TARGET_SKILLS.split(",") if skill.strip()]

    @property
    def telegram_enabled(self) -> bool:
        """Check if Telegram notifications are configured."""
        return bool(self.TELEGRAM_BOT_TOKEN and self.TELEGRAM_CHAT_ID)

    class Config:
        # Tell Pydantic to read from .env file (project root)
        env_file = os.path.join(os.path.dirname(__file__), "..", ".env")
        env_file_encoding = "utf-8"
        # Allow extra fields (future-proofing)
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """
    Create and cache the Settings instance.
    
    Using @lru_cache ensures we only read .env once,
    and all imports get the same Settings object.
    
    Usage:
        from config import settings
        print(settings.ANTHROPIC_API_KEY)
    """
    return Settings()


# ─────────────────────────────────────
# Global settings instance
# Import this in other modules:
#   from config import settings
# ─────────────────────────────────────
settings = get_settings()
