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
║  4. Access values: settings.MONGODB_URI                           ║
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

    # MongoDB connection
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "jobpilot"

    # ─────────────────────────────────────
    # JOB SEARCH DEFAULTS (overridden per user in MongoDB)
    # ─────────────────────────────────────

    TARGET_ROLES: str = "Software Engineer"
    TARGET_EXPERIENCE_MIN: float = 0
    TARGET_EXPERIENCE_MAX: float = 5
    TARGET_LOCATIONS: str = "Remote"
    TARGET_SKILLS: str = ""

    # ─────────────────────────────────────
    # TELEGRAM NOTIFICATIONS (optional)
    # ─────────────────────────────────────

    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""

    # ─────────────────────────────────────
    # SCHEDULER
    # ─────────────────────────────────────

    SCRAPE_INTERVAL_HOURS: int = 6
    AUTO_APPLY_ENABLED: bool = False
    AUTO_APPLY_MODE: str = "semi"
    MIN_MATCH_SCORE_TO_APPLY: int = 70

    # ─────────────────────────────────────
    # AUTH / JWT
    # ─────────────────────────────────────

    JWT_SECRET_KEY: str = "jobpilot-super-secret-change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_HOURS: int = 72

    # ─────────────────────────────────────
    # SERVER
    # ─────────────────────────────────────

    LOG_LEVEL: str = "INFO"
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:5173"

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
        print(settings.MONGODB_URI)
    """
    return Settings()


# ─────────────────────────────────────
# Global settings instance
# Import this in other modules:
#   from config import settings
# ─────────────────────────────────────
settings = get_settings()
