"""
╔═══════════════════════════════════════════════════════════════════╗
║  JOBPILOT — FastAPI Application Entry Point                      ║
║                                                                   ║
║  This is the main file that ties everything together:             ║
║  - Creates the FastAPI app                                       ║
║  - Connects to MongoDB on startup                                ║
║  - Starts the background scheduler                               ║
║  - Registers all API routers                                     ║
║  - Configures CORS for the frontend                              ║
║  - Serves static files (resume PDFs)                             ║
║                                                                   ║
║  RUN:                                                             ║
║    uvicorn main:app --reload --port 8000                         ║
║                                                                   ║
║  DOCS:                                                            ║
║    http://localhost:8000/docs     (Swagger UI)                   ║
║    http://localhost:8000/redoc    (ReDoc)                         ║
╚═══════════════════════════════════════════════════════════════════╝
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import settings
from database import connect_db, close_db
from schedulers.job_scheduler import start_scheduler, stop_scheduler
from utils.logger import logger

# Import routers
from routers.jobs import router as jobs_router
from routers.applications import router as applications_router
from routers.resumes import router as resumes_router
from routers.dashboard import router as dashboard_router
from routers.settings import router as settings_router


# ─────────────────────────────────────
# Application Lifespan
# Runs startup/shutdown logic
# ─────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    
    ON STARTUP:
    1. Connect to MongoDB
    2. Start the background scheduler
    3. Ensure data directories exist
    
    ON SHUTDOWN:
    1. Stop the scheduler
    2. Close MongoDB connection
    """
    # ── STARTUP ──
    logger.info("🚀 Starting JobPilot...")

    # Ensure required directories exist
    os.makedirs("logs", exist_ok=True)
    os.makedirs(os.path.join("..", "data", "resumes"), exist_ok=True)
    os.makedirs(os.path.join("..", "data", "cover_letters"), exist_ok=True)

    # Connect to MongoDB
    await connect_db()

    # Start background scheduler
    start_scheduler()

    logger.info("✅ JobPilot is ready!")
    logger.info(f"   API Docs: http://localhost:{settings.BACKEND_PORT}/docs")
    logger.info(f"   Dashboard: {settings.FRONTEND_URL}")

    yield  # App is running

    # ── SHUTDOWN ──
    logger.info("Shutting down JobPilot...")
    stop_scheduler()
    await close_db()
    logger.info("👋 JobPilot stopped")


# ─────────────────────────────────────
# Create the FastAPI Application
# ─────────────────────────────────────
app = FastAPI(
    title="JobPilot API",
    description=(
        "AI-powered automated job application engine. "
        "Scrapes jobs, tailors resumes, and auto-applies."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",     # Swagger UI
    redoc_url="/redoc",   # ReDoc
)


# ─────────────────────────────────────
# CORS Middleware
# Allows the React frontend to talk to the API
# ─────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:5173",   # Vite default
        "http://localhost:3000",   # Common React port
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],           # Allow all HTTP methods
    allow_headers=["*"],           # Allow all headers
)


# ─────────────────────────────────────
# Register API Routers
# ─────────────────────────────────────
app.include_router(jobs_router)
app.include_router(applications_router)
app.include_router(resumes_router)
app.include_router(dashboard_router)
app.include_router(settings_router)


# ─────────────────────────────────────
# Static File Serving (resume/cover letter PDFs)
# ─────────────────────────────────────
data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
if os.path.exists(data_dir):
    app.mount("/static/data", StaticFiles(directory=data_dir), name="data")


# ─────────────────────────────────────
# Root Endpoint
# ─────────────────────────────────────
@app.get("/", tags=["Health"])
async def root():
    """Root endpoint — basic API info."""
    return {
        "name": "JobPilot API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }
