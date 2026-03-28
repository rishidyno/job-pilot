"""
User preferences — reads from MongoDB user_profile collection.
Falls back to .env defaults if no profile exists yet.
All user-specific config should go through this module.
"""

from database import get_collection
from config import settings


async def get_user_prefs() -> dict:
    """
    Get the current user's preferences from MongoDB.
    Falls back to .env defaults for missing fields.
    """
    col = get_collection("user_profile")
    profile = await col.find_one({})

    defaults = {
        "target_roles": settings.target_roles_list,
        "target_locations": settings.target_locations_list,
        "primary_skills": settings.target_skills_list,
        "target_experience_min": settings.TARGET_EXPERIENCE_MIN,
        "target_experience_max": settings.TARGET_EXPERIENCE_MAX,
        "min_match_score": settings.MIN_MATCH_SCORE_TO_APPLY,
        "auto_apply_enabled": settings.AUTO_APPLY_ENABLED,
        "auto_apply_mode": settings.AUTO_APPLY_MODE,
        "scrape_interval_hours": settings.SCRAPE_INTERVAL_HOURS,
        "telegram_bot_token": settings.TELEGRAM_BOT_TOKEN,
        "telegram_chat_id": settings.TELEGRAM_CHAT_ID,
        # Portal credentials — empty by default, user sets via UI
        "portal_credentials": {},
    }

    if not profile:
        return defaults

    # Merge: profile values override defaults, skip None/empty
    merged = {**defaults}
    for key in defaults:
        val = profile.get(key)
        if val is not None and val != "" and val != []:
            merged[key] = val

    return merged
