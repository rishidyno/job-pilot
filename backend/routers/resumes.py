"""
JOBPILOT — Resumes API Router (LaTeX-based)

Endpoints:
  GET    /api/resumes/latex          → Get base LaTeX source
  PUT    /api/resumes/latex          → Update base LaTeX source
  GET    /api/resumes                → List all resume versions
  GET    /api/resumes/:id            → Get a specific resume
  POST   /api/resumes/tailor         → Tailor resume for a job (AI modifies LaTeX)
  GET    /api/resumes/compile/:id    → Compile LaTeX → PDF and serve
  POST   /api/resumes/cover-letter   → Generate cover letter
"""

import os
import asyncio
import tempfile
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import Response
from bson import ObjectId
from pydantic import BaseModel
from database import get_collection
from services.resume_tailor import resume_tailor
from services.cover_letter_service import cover_letter_service
from services.job_matcher import job_matcher
from services.auth_service import get_current_user_id
from utils.helpers import utc_now
from utils.logger import logger

router = APIRouter(prefix="/api/resumes", tags=["Resumes"])

import shutil

_default_pdflatex = shutil.which("pdflatex") or "/Library/TeX/texbin/pdflatex"
PDFLATEX_PATH = os.environ.get("PDFLATEX_PATH", _default_pdflatex)
HAS_PDFLATEX = os.path.isfile(PDFLATEX_PATH) if PDFLATEX_PATH else False


class LatexContent(BaseModel):
    content: str


async def _compile_latex(latex_source: str) -> bytes:
    """Compile LaTeX to PDF. Uses local pdflatex if available, else remote API."""
    if HAS_PDFLATEX:
        return await _compile_local(latex_source)
    return await _compile_remote(latex_source)


async def _compile_local(latex_source: str) -> bytes:
    """Compile using local pdflatex."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tex_path = os.path.join(tmpdir, "resume.tex")
        with open(tex_path, "w") as f:
            f.write(latex_source)

        proc = await asyncio.create_subprocess_exec(
            PDFLATEX_PATH, "-interaction=nonstopmode", "resume.tex",
            cwd=tmpdir,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await asyncio.wait_for(proc.communicate(), timeout=30)

        pdf_path = os.path.join(tmpdir, "resume.pdf")
        if not os.path.exists(pdf_path):
            raise RuntimeError("LaTeX compilation failed — no PDF produced")

        with open(pdf_path, "rb") as f:
            return f.read()


async def _compile_remote(latex_source: str) -> bytes:
    """Compile using remote LaTeX API (latex.ytotech.com)."""
    import httpx
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                "https://latex.ytotech.com/builds/sync",
                json={
                    "compiler": "pdflatex",
                    "resources": [{"main": True, "content": latex_source}],
                },
            )
            if resp.status_code == 200 and resp.headers.get("content-type", "").startswith("application/pdf"):
                return resp.content
            raise RuntimeError(f"Remote LaTeX API error: {resp.status_code}")
    except Exception as e:
        raise RuntimeError(f"LaTeX compilation unavailable: {str(e)[:100]}. Install pdflatex locally for PDF preview.")


@router.get("/latex")
async def get_latex(user_id: str = Depends(get_current_user_id)):
    """Get the user's base LaTeX resume source."""
    resumes_col = get_collection("resumes")
    # Prefer the one with latex_source
    resume = await resumes_col.find_one({"user_id": user_id, "is_base": True, "latex_source": {"$exists": True, "$ne": ""}})
    if not resume:
        resume = await resumes_col.find_one({"user_id": user_id, "is_base": True})
    return {"content": resume.get("latex_source", "") if resume else ""}


@router.put("/latex")
async def update_latex(data: LatexContent, user_id: str = Depends(get_current_user_id)):
    """Update the user's base LaTeX resume source."""
    resumes_col = get_collection("resumes")
    # Find existing base with latex, or any base, or create new
    existing = await resumes_col.find_one({"user_id": user_id, "is_base": True, "latex_source": {"$exists": True}})
    if existing:
        await resumes_col.update_one({"_id": existing["_id"]}, {"$set": {"latex_source": data.content, "updated_at": utc_now()}})
    else:
        await resumes_col.update_one(
            {"user_id": user_id, "is_base": True},
            {"$set": {"latex_source": data.content, "is_base": True, "updated_at": utc_now()}},
            upsert=True,
        )
    return {"success": True}


@router.get("")
async def list_resumes(
    job_id: Optional[str] = Query(None),
    is_base: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    user_id: str = Depends(get_current_user_id),
):
    """List all resume versions."""
    resumes_col = get_collection("resumes")
    query = {"user_id": user_id}
    if job_id:
        query["job_id"] = job_id
    if is_base is not None:
        query["is_base"] = is_base

    cursor = resumes_col.find(query, {"latex_source": 0}).sort("created_at", -1).skip(skip).limit(limit)
    resumes = await cursor.to_list(limit)
    total = await resumes_col.count_documents(query)

    for r in resumes:
        r["_id"] = str(r["_id"])

    return {"resumes": resumes, "total": total}


@router.get("/{resume_id}")
async def get_resume(resume_id: str, user_id: str = Depends(get_current_user_id)):
    """Get a specific resume by ID."""
    resumes_col = get_collection("resumes")
    try:
        resume = await resumes_col.find_one({"_id": ObjectId(resume_id), "user_id": user_id})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid resume ID")
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    resume["_id"] = str(resume["_id"])
    return resume


@router.post("/tailor")
async def tailor_resume(job_id: str, user_id: str = Depends(get_current_user_id)):
    """Tailor resume for a specific job. Fetches job description if missing."""
    jobs_col = get_collection("jobs")
    resumes_col = get_collection("resumes")

    job = await jobs_col.find_one({"_id": ObjectId(job_id), "user_id": user_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    base = await resumes_col.find_one({"is_base": True, "user_id": user_id})
    if not base or not base.get("latex_source"):
        raise HTTPException(status_code=400, detail="No base LaTeX resume found. Upload one first.")

    # If job has no description, try to fetch it from the portal
    description = job.get("description", "") or ""
    skills = job.get("skills", []) or []

    if not description and job.get("url"):
        try:
            from scrapers.scraper_manager import SCRAPERS
            portal = job.get("portal", "")
            if portal in SCRAPERS:
                scraper = SCRAPERS[portal]()
                await scraper.launch_browser()
                try:
                    detail = await scraper.parse_job_detail(job["url"])
                    if detail:
                        description = detail.get("description", "") or ""
                        skills = detail.get("skills", skills) or skills
                        # Save fetched data back to job
                        update = {}
                        if description:
                            update["description"] = description
                        if detail.get("skills"):
                            update["skills"] = detail["skills"]
                        if update:
                            update["updated_at"] = utc_now()
                            await jobs_col.update_one({"_id": job["_id"]}, {"$set": update})
                            logger.info(f"Fetched job description for '{job['title']}' ({len(description)} chars)")
                finally:
                    await scraper.close_browser()
        except Exception as e:
            logger.warning(f"Failed to fetch job description: {e}")

    try:
        result = await resume_tailor.tailor_resume(
            latex_source=base["latex_source"],
            job_title=job["title"],
            job_description=description,
            job_skills=skills,
            company_name=job["company"],
            user_id=user_id,
        )
    except Exception as e:
        logger.error(f"AI tailoring failed: {e}")
        raise HTTPException(status_code=500, detail=f"AI tailoring failed: {str(e)[:200]}")

    # Save tailored version with job context for easy reference
    resume_doc = {
        "is_base": False,
        "user_id": user_id,
        "job_id": job_id,
        "job_title": job["title"],
        "job_company": job["company"],
        "job_url": job.get("url", ""),
        "job_portal": job.get("portal", ""),
        "job_match_score": job.get("match_score"),
        "latex_source": result["latex_source"],
        "changes_made": result.get("changes_made", []),
        "created_at": utc_now(),
    }
    insert = await resumes_col.insert_one(resume_doc)

    # Re-score the job now that we have a tailored resume
    from services.user_prefs import get_user_prefs
    prefs = await get_user_prefs(user_id)
    new_score = await job_matcher.quick_score(
        job_title=job["title"],
        job_skills=skills or [],
        job_location=job.get("location", ""),
        user_skills=prefs["primary_skills"],
        user_target_locations=prefs["target_locations"],
    )
    # Boost score slightly since resume is now tailored for this job
    new_score = min(100, new_score + 5)

    await jobs_col.update_one(
        {"_id": ObjectId(job_id), "user_id": user_id},
        {"$set": {
            "tailored_resume_id": str(insert.inserted_id),
            "match_score": new_score,
            "updated_at": utc_now(),
        }}
    )

    return {
        "success": True,
        "resume_id": str(insert.inserted_id),
        "changes_made": result.get("changes_made", []),
        "new_score": new_score,
    }


@router.get("/compile/{resume_id}")
async def compile_resume(resume_id: str, token: Optional[str] = None):
    """Compile LaTeX to PDF and serve. Falls back to uploaded PDF file."""
    from services.auth_service import decode_token
    if not token:
        raise HTTPException(status_code=401, detail="Token required")
    user_id = decode_token(token)

    resumes_col = get_collection("resumes")
    resume = await resumes_col.find_one({"_id": ObjectId(resume_id), "user_id": user_id})
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    # Primary: compile LaTeX
    latex = resume.get("latex_source", "")
    if latex:
        try:
            pdf_bytes = await _compile_latex(latex)
            return Response(content=pdf_bytes, media_type="application/pdf",
                            headers={"Content-Disposition": "inline"})
        except Exception as e:
            logger.error(f"LaTeX compilation failed: {e}")
            raise HTTPException(status_code=500, detail=f"Compilation failed: {str(e)[:200]}")

    # Fallback: serve uploaded PDF file
    file_path = resume.get("file_path_original_style", "")
    if file_path and os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return Response(content=f.read(), media_type="application/pdf",
                            headers={"Content-Disposition": "inline"})

    raise HTTPException(status_code=400, detail="No LaTeX source or PDF file found. Edit your resume in the LaTeX editor first.")


@router.post("/cover-letter")
async def generate_cover_letter(job_id: str, tone: str = "professional", user_id: str = Depends(get_current_user_id)):
    """Generate a cover letter for a specific job."""
    jobs_col = get_collection("jobs")
    resumes_col = get_collection("resumes")
    cl_col = get_collection("cover_letters")

    job = await jobs_col.find_one({"_id": ObjectId(job_id), "user_id": user_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    base = await resumes_col.find_one({"is_base": True, "user_id": user_id})
    resume_text = base.get("latex_source", "") if base else ""

    letter = await cover_letter_service.generate(
        resume_text=resume_text,
        job_title=job["title"],
        job_description=job.get("description", ""),
        company_name=job["company"],
        tone=tone,
    )

    cl_doc = {
        "job_id": job_id,
        "user_id": user_id,
        "content": letter.get("full_text", ""),
        "tone": tone,
        "created_at": utc_now(),
    }
    result = await cl_col.insert_one(cl_doc)

    return {
        "success": True,
        "cover_letter_id": str(result.inserted_id),
        "content": letter.get("full_text", ""),
    }
