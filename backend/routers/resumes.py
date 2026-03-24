"""
╔═══════════════════════════════════════════════════════════════════╗
║  JOBPILOT — Resumes API Router                                   ║
║                                                                   ║
║  Endpoints for managing resumes and cover letters:                ║
║  POST   /api/resumes/upload-base    → Upload your base resume    ║
║  GET    /api/resumes                → List all resume versions   ║
║  GET    /api/resumes/:id            → Get a specific resume      ║
║  POST   /api/resumes/tailor         → Tailor resume for a job   ║
║  POST   /api/resumes/cover-letter   → Generate cover letter      ║
║  GET    /api/resumes/download/:id   → Download resume PDF        ║
╚═══════════════════════════════════════════════════════════════════╝
"""

import os
import asyncio
import aiofiles
from typing import Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Query
from fastapi.responses import FileResponse
from bson import ObjectId
from database import get_collection
from services.resume_tailor import resume_tailor
from services.cover_letter_service import cover_letter_service
from services.pdf_generator import pdf_generator
from config import settings
from utils.helpers import utc_now
from utils.logger import logger

router = APIRouter(prefix="/api/resumes", tags=["Resumes"])

# Path for storing base resume
BASE_RESUME_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "resumes"))


@router.post("/upload-base")
async def upload_base_resume(file: UploadFile = File(...)):
    """
    Upload your base resume (PDF).
    
    This is the source-of-truth resume that all tailored versions
    derive from. Only one base resume exists at a time — uploading
    a new one replaces the old one.
    
    The PDF text is extracted and stored for AI processing.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    resumes_col = get_collection("resumes")

    # Save the file
    os.makedirs(BASE_RESUME_DIR, exist_ok=True)
    file_path = os.path.join(BASE_RESUME_DIR, file.filename)

    async with aiofiles.open(file_path, "wb") as f:
        content = await file.read()
        await f.write(content)

    # Extract text from PDF (non-blocking)
    raw_text = ""
    try:
        proc = await asyncio.create_subprocess_exec(
            "pdftotext", file_path, "-",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=10)
        raw_text = stdout.decode("utf-8").strip()
    except Exception as e:
        logger.warning(f"pdftotext failed: {e}")
        raw_text = ""

    # Upsert base resume in DB (replace existing base)
    await resumes_col.update_one(
        {"is_base": True},
        {"$set": {
            "is_base": True,
            "file_path_original_style": file_path,
            "original_filename": file.filename,
            "raw_text": raw_text,
            "created_at": utc_now(),
            "content_json": None,
            "job_id": None,
        }},
        upsert=True,
    )

    logger.info(f"Base resume uploaded: {file.filename} ({len(raw_text)} chars extracted)")

    return {
        "success": True,
        "message": "Base resume uploaded successfully",
        "text_length": len(raw_text),
        "file_path": file_path,
    }


@router.get("")
async def list_resumes(
    job_id: Optional[str] = Query(None, description="Filter by job ID"),
    is_base: Optional[bool] = Query(None, description="Filter base vs tailored"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    """List all resume versions."""
    resumes_col = get_collection("resumes")
    query = {}
    if job_id:
        query["job_id"] = job_id
    if is_base is not None:
        query["is_base"] = is_base

    cursor = resumes_col.find(query).sort("created_at", -1).skip(skip).limit(limit)
    resumes = await cursor.to_list(limit)
    total = await resumes_col.count_documents(query)

    for r in resumes:
        r["_id"] = str(r["_id"])

    return {"resumes": resumes, "total": total}


@router.get("/{resume_id}")
async def get_resume(resume_id: str):
    """Get a specific resume by ID."""
    resumes_col = get_collection("resumes")
    try:
        resume = await resumes_col.find_one({"_id": ObjectId(resume_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid resume ID")
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    resume["_id"] = str(resume["_id"])
    return resume


@router.post("/tailor")
async def tailor_resume(job_id: str):
    """
    Generate a tailored resume for a specific job.
    
    Takes the base resume, sends it to Claude with the job description,
    and generates two PDF versions (original style + clean template).
    """
    jobs_col = get_collection("jobs")
    resumes_col = get_collection("resumes")

    # Get the job
    job = await jobs_col.find_one({"_id": ObjectId(job_id)})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Get base resume
    base_resume = await resumes_col.find_one({"is_base": True})
    if not base_resume:
        raise HTTPException(status_code=400, detail="No base resume found. Upload one first.")

    # Tailor with AI
    tailored = await resume_tailor.tailor_resume(
        base_resume_text=base_resume.get("raw_text", ""),
        job_title=job["title"],
        job_description=job.get("description", ""),
        job_skills=job.get("skills", []),
        company_name=job["company"],
    )

    # Generate PDFs
    pdf_original = await pdf_generator.generate_resume_pdf(
        content=tailored, template_style="original",
        job_title=job["title"], company_name=job["company"],
    )
    pdf_clean = await pdf_generator.generate_resume_pdf(
        content=tailored, template_style="clean",
        job_title=job["title"], company_name=job["company"],
    )

    # Save to DB
    resume_doc = {
        "is_base": False,
        "job_id": job_id,
        "base_resume_id": str(base_resume["_id"]),
        "content_json": tailored,
        "file_path_original_style": pdf_original,
        "file_path_clean_style": pdf_clean,
        "ai_model_used": tailored.get("_ai_metadata", {}).get("model"),
        "changes_made": tailored.get("changes_made", []),
        "created_at": utc_now(),
    }
    result = await resumes_col.insert_one(resume_doc)

    # Link tailored resume back to the job
    await jobs_col.update_one(
        {"_id": ObjectId(job_id)},
        {"$set": {"tailored_resume_id": str(result.inserted_id), "updated_at": utc_now()}}
    )

    return {
        "success": True,
        "resume_id": str(result.inserted_id),
        "changes_made": tailored.get("changes_made", []),
        "pdf_original": pdf_original,
        "pdf_clean": pdf_clean,
    }


@router.post("/cover-letter")
async def generate_cover_letter(job_id: str, tone: str = "professional"):
    """Generate a cover letter for a specific job."""
    jobs_col = get_collection("jobs")
    resumes_col = get_collection("resumes")
    cl_col = get_collection("cover_letters")

    job = await jobs_col.find_one({"_id": ObjectId(job_id)})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    base_resume = await resumes_col.find_one({"is_base": True})
    resume_text = base_resume.get("raw_text", "") if base_resume else ""

    # Generate with AI
    letter = await cover_letter_service.generate(
        resume_text=resume_text,
        job_title=job["title"],
        job_description=job.get("description", ""),
        company_name=job["company"],
        tone=tone,
    )

    # Generate PDF
    pdf_path = await pdf_generator.generate_cover_letter_pdf(
        content=letter, job_title=job["title"], company_name=job["company"],
    )

    # Save to DB
    cl_doc = {
        "job_id": job_id,
        "content": letter.get("full_text", ""),
        "file_path": pdf_path,
        "tone": tone,
        "created_at": utc_now(),
    }
    result = await cl_col.insert_one(cl_doc)

    return {
        "success": True,
        "cover_letter_id": str(result.inserted_id),
        "content": letter.get("full_text", ""),
        "pdf_path": pdf_path,
    }


@router.get("/download/{resume_id}")
async def download_resume(resume_id: str, style: str = "original", preview: bool = False):
    """Download or preview a resume PDF file."""
    resumes_col = get_collection("resumes")
    resume = await resumes_col.find_one({"_id": ObjectId(resume_id)})

    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    file_key = "file_path_original_style" if style == "original" else "file_path_clean_style"
    file_path = resume.get(file_key)

    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="PDF file not found")

    from starlette.responses import Response
    if preview:
        with open(file_path, "rb") as f:
            content = f.read()
        return Response(content, media_type="application/pdf", headers={"Content-Disposition": "inline"})

    return FileResponse(file_path, media_type="application/pdf", filename=os.path.basename(file_path))
