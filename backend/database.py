"""
╔═══════════════════════════════════════════════════════════════════╗
║  JOBPILOT — Database Layer (MongoDB via Motor)                   ║
║                                                                   ║
║  This module manages the async MongoDB connection using Motor.    ║
║  Motor is the async driver for MongoDB, built on top of PyMongo.  ║
║                                                                   ║
║  COLLECTIONS:                                                     ║
║  ┌──────────────────┬────────────────────────────────────────┐   ║
║  │ jobs              │ Scraped job listings from all portals  │   ║
║  │ applications      │ Tracked job applications & statuses   │   ║
║  │ resumes           │ Base + tailored resume metadata       │   ║
║  │ cover_letters     │ Generated cover letter metadata       │   ║
║  │ user_profile      │ User's profile & preferences         │   ║
║  │ scrape_logs       │ Scraper run history & stats          │   ║
║  └──────────────────┴────────────────────────────────────────┘   ║
║                                                                   ║
║  USAGE:                                                           ║
║    from database import get_db, get_collection                    ║
║    db = get_db()                                                  ║
║    jobs = get_collection("jobs")                                  ║
║    await jobs.find({"status": "new"}).to_list(100)                ║
║                                                                   ║
║  LIFECYCLE:                                                       ║
║    connect_db() is called on app startup (in main.py)             ║
║    close_db() is called on app shutdown (in main.py)              ║
╚═══════════════════════════════════════════════════════════════════╝
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from config import settings
from utils.logger import logger

# ─────────────────────────────────────
# Module-level state
# These are set by connect_db() and cleared by close_db()
# ─────────────────────────────────────
_client: AsyncIOMotorClient | None = None
_database: AsyncIOMotorDatabase | None = None


async def connect_db() -> None:
    """
    Establish connection to MongoDB.
    
    Called once during app startup (see main.py lifespan).
    Creates the Motor client and verifies connectivity with a ping.
    Also creates necessary indexes for performance.
    
    Raises:
        Exception: If MongoDB is unreachable
    """
    global _client, _database

    logger.info(f"Connecting to MongoDB at {settings.MONGODB_URI}...")

    import certifi

    # Create the async Motor client
    # maxPoolSize controls how many concurrent connections we allow
    _client = AsyncIOMotorClient(
        settings.MONGODB_URI,
        maxPoolSize=50,           # Max concurrent connections
        minPoolSize=5,            # Keep at least 5 connections warm
        serverSelectionTimeoutMS=5000,  # Fail fast if MongoDB is down
        tlsCAFile=certifi.where(),     # CA bundle for Atlas SSL
    )

    # Select the database
    _database = _client[settings.MONGODB_DB_NAME]

    # Verify connection with a ping
    try:
        await _client.admin.command("ping")
        logger.info(f"✅ Connected to MongoDB database: {settings.MONGODB_DB_NAME}")
    except Exception as e:
        logger.error(f"❌ Failed to connect to MongoDB: {e}")
        raise

    # Create indexes for commonly queried fields
    await _create_indexes()


async def _create_indexes() -> None:
    """
    Create MongoDB indexes for performance.
    
    All data is scoped per user, so most indexes include user_id
    as the leading field for efficient per-user queries.
    """
    db = get_db()

    # ── Drop old single-tenant indexes that conflict with multi-user ──
    for col_name, old_indexes in [
        ("jobs", ["unique_job_per_portal"]),
        ("applications", ["one_app_per_job"]),
    ]:
        col = db[col_name]
        existing = await col.index_information()
        for idx_name in old_indexes:
            if idx_name in existing:
                await col.drop_index(idx_name)
                logger.info(f"Dropped old index {col_name}.{idx_name}")

    # ── Jobs collection indexes ──
    # Unique per user: same job from same portal per user
    await db.jobs.create_index(
        [("user_id", 1), ("portal", 1), ("external_id", 1)],
        unique=True,
        name="unique_job_per_user_portal"
    )
    # Per-user queries sorted by match score
    await db.jobs.create_index(
        [("user_id", 1), ("match_score", -1)],
        name="user_match_score"
    )
    # Per-user queries sorted by date
    await db.jobs.create_index(
        [("user_id", 1), ("created_at", -1)],
        name="user_created_at"
    )
    # Per-user status filter
    await db.jobs.create_index(
        [("user_id", 1), ("status", 1)],
        name="user_status"
    )
    # Text index (can't include user_id, MongoDB limitation — filtered in app layer)
    try:
        await db.jobs.create_index(
            [("title", "text"), ("company", "text"), ("description", "text")],
            name="job_text_search"
        )
    except Exception:
        pass  # Already exists

    # ── Applications collection indexes ──
    # Unique: one application per job per user
    await db.applications.create_index(
        [("user_id", 1), ("job_id", 1)],
        unique=True,
        name="one_app_per_user_job"
    )
    await db.applications.create_index(
        [("user_id", 1), ("status", 1)],
        name="user_app_status"
    )
    await db.applications.create_index(
        [("user_id", 1), ("applied_at", -1)],
        name="user_app_date"
    )

    # ── Resumes collection indexes ──
    await db.resumes.create_index(
        [("user_id", 1), ("is_base", 1)],
        name="user_base_resume"
    )
    await db.resumes.create_index(
        [("user_id", 1), ("job_id", 1)],
        name="user_resume_job"
    )

    # ── User profile — one per user ──
    await db.user_profile.create_index(
        [("user_id", 1)],
        unique=True,
        name="unique_user_profile"
    )

    # ── Cover letters ──
    await db.cover_letters.create_index(
        [("user_id", 1), ("job_id", 1)],
        name="user_cover_letter_job"
    )

    # ── Scrape logs ──
    await db.scrape_logs.create_index([("user_id", 1), ("started_at", -1)], name="user_scrape_log")

    # ── Users ──
    await db.users.create_index([("email", 1)], unique=True, name="unique_email")

    logger.info("✅ Database indexes created/verified")


async def close_db() -> None:
    """
    Close the MongoDB connection gracefully.
    
    Called during app shutdown (see main.py lifespan).
    Always call this to prevent connection leaks.
    """
    global _client, _database

    if _client:
        _client.close()
        _client = None
        _database = None
        logger.info("MongoDB connection closed")


def get_db() -> AsyncIOMotorDatabase:
    """
    Get the current database instance.
    
    Usage:
        db = get_db()
        result = await db.jobs.find_one({"_id": job_id})
    
    Returns:
        AsyncIOMotorDatabase: The active database connection
    
    Raises:
        RuntimeError: If called before connect_db()
    """
    if _database is None:
        raise RuntimeError(
            "Database not initialized. Call connect_db() first. "
            "This usually means the app hasn't started yet."
        )
    return _database


def get_collection(name: str):
    """
    Get a specific MongoDB collection by name.
    
    Convenience wrapper around get_db()[name].
    
    Args:
        name: Collection name (e.g., "jobs", "applications", "resumes")
    
    Returns:
        AsyncIOMotorCollection: The collection object
    
    Usage:
        jobs = get_collection("jobs")
        await jobs.insert_one({"title": "SDE-2", "company": "Google"})
    """
    return get_db()[name]
