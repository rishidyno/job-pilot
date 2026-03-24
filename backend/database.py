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

    # Create the async Motor client
    # maxPoolSize controls how many concurrent connections we allow
    _client = AsyncIOMotorClient(
        settings.MONGODB_URI,
        maxPoolSize=50,           # Max concurrent connections
        minPoolSize=5,            # Keep at least 5 connections warm
        serverSelectionTimeoutMS=5000,  # Fail fast if MongoDB is down
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
    
    Indexes are idempotent — calling this multiple times is safe.
    MongoDB will skip index creation if the index already exists.
    
    WHY THESE INDEXES:
    - jobs.portal + jobs.external_id: Unique constraint to prevent duplicate job entries
    - jobs.match_score: Fast sorting by relevance
    - jobs.created_at: Fast date-range queries
    - applications.status: Fast filtering by application status
    - applications.job_id: Fast lookup of application by job
    """
    db = get_db()

    # ── Jobs collection indexes ──
    # Unique index: same job from same portal should not be duplicated
    await db.jobs.create_index(
        [("portal", 1), ("external_id", 1)],
        unique=True,
        name="unique_job_per_portal"
    )
    # Sort by match score for "best matches first" queries
    await db.jobs.create_index([("match_score", -1)], name="match_score_desc")
    # Sort by creation date for "newest first" queries
    await db.jobs.create_index([("created_at", -1)], name="created_at_desc")
    # Filter by status (new, reviewed, applied, rejected, etc.)
    await db.jobs.create_index([("status", 1)], name="status_filter")
    # Text index for full-text search across job titles and descriptions
    await db.jobs.create_index(
        [("title", "text"), ("company", "text"), ("description", "text")],
        name="job_text_search"
    )

    # ── Applications collection indexes ──
    await db.applications.create_index([("status", 1)], name="app_status_filter")
    await db.applications.create_index([("job_id", 1)], unique=True, name="one_app_per_job")
    await db.applications.create_index([("applied_at", -1)], name="app_date_desc")

    # ── Resumes collection indexes ──
    await db.resumes.create_index([("job_id", 1)], name="resume_by_job")
    await db.resumes.create_index([("is_base", 1)], name="base_resume_filter")

    # ── Scrape logs ──
    await db.scrape_logs.create_index([("started_at", -1)], name="scrape_log_date")

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
