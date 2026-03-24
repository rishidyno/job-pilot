"""
╔═══════════════════════════════════════════════════════════════════╗
║  JOBPILOT — Applier Manager                                      ║
║                                                                   ║
║  Orchestrates the auto-apply pipeline:                            ║
║  1. Find jobs that are ready to apply (shortlisted + high score) ║
║  2. Generate tailored resume + cover letter                      ║
║  3. Use the appropriate portal applier to submit                 ║
║  4. Track the application in MongoDB                             ║
║  5. Send notifications                                           ║
║                                                                   ║
║  Supports TWO MODES:                                              ║
║  - "auto": Fully automatic — applies without human review        ║
║  - "semi": Queues jobs for review — user clicks "Apply" on dash  ║
╚═══════════════════════════════════════════════════════════════════╝
"""

from typing import Optional, Dict
from bson import ObjectId

from appliers.base_applier import BaseApplier
from appliers.linkedin_applier import LinkedInApplier
from appliers.naukri_applier import NaukriApplier
from appliers.wellfound_applier import WellfoundApplier
from appliers.instahyre_applier import InstahyreApplier

from services.resume_tailor import resume_tailor
from services.cover_letter_service import cover_letter_service
from services.pdf_generator import pdf_generator
from services.telegram_service import telegram_service
from database import get_collection
from config import settings
from utils.logger import logger
from utils.helpers import utc_now


# ─────────────────────────────────────
# APPLIER REGISTRY
# Maps portal name → applier class
# Add new appliers here!
# ─────────────────────────────────────
APPLIERS: Dict[str, type] = {
    "linkedin": LinkedInApplier,
    "naukri": NaukriApplier,
    "wellfound": WellfoundApplier,
    "instahyre": InstahyreApplier,
}


class ApplierManager:
    """
    Manages the full auto-apply pipeline.
    
    This is called by:
    - The scheduler (for auto-mode jobs)
    - The API (when user clicks "Apply" in semi-mode)
    """

    async def apply_to_job(self, job_id: str, force: bool = False) -> dict:
        """
        Apply to a specific job.
        
        Full pipeline:
        1. Fetch job from DB
        2. Get base resume text
        3. Tailor resume for this job
        4. Generate cover letter
        5. Generate PDFs (both styles)
        6. Use portal-specific applier to submit
        7. Create application record
        8. Send notification
        
        Args:
            job_id: MongoDB ObjectId of the job
            force: If True, skip match score check
        
        Returns:
            dict: Application result {success, application_id, error}
        """
        jobs_col = get_collection("jobs")
        apps_col = get_collection("applications")
        resumes_col = get_collection("resumes")

        # ── Step 1: Fetch the job ──
        job = await jobs_col.find_one({"_id": ObjectId(job_id)})
        if not job:
            return {"success": False, "error": f"Job {job_id} not found"}

        # Check if already applied
        existing_app = await apps_col.find_one({"job_id": job_id})
        if existing_app:
            return {"success": False, "error": "Already applied to this job"}

        # Check match score threshold (unless forced)
        if not force and (job.get("match_score", 0) < settings.MIN_MATCH_SCORE_TO_APPLY):
            return {
                "success": False,
                "error": f"Match score {job.get('match_score', 0)} below threshold {settings.MIN_MATCH_SCORE_TO_APPLY}",
            }

        portal = job.get("portal", "unknown")
        logger.info(f"Starting apply pipeline for '{job['title']}' at {job['company']} via {portal}")

        try:
            # ── Step 2: Get base resume ──
            base_resume = await resumes_col.find_one({"is_base": True})
            if not base_resume:
                return {"success": False, "error": "No base resume found. Upload one first."}

            resume_text = base_resume.get("raw_text", "")

            # ── Step 3: Tailor resume ──
            tailored_content = await resume_tailor.tailor_resume(
                base_resume_text=resume_text,
                job_title=job["title"],
                job_description=job.get("description", ""),
                job_skills=job.get("skills", []),
                company_name=job["company"],
            )

            # ── Step 4: Generate cover letter ──
            cover_letter_content = await cover_letter_service.generate(
                resume_text=resume_text,
                job_title=job["title"],
                job_description=job.get("description", ""),
                company_name=job["company"],
            )

            # ── Step 5: Generate PDFs ──
            resume_pdf_original = await pdf_generator.generate_resume_pdf(
                content=tailored_content, template_style="original",
                job_title=job["title"], company_name=job["company"],
            )
            resume_pdf_clean = await pdf_generator.generate_resume_pdf(
                content=tailored_content, template_style="clean",
                job_title=job["title"], company_name=job["company"],
            )
            cover_letter_pdf = await pdf_generator.generate_cover_letter_pdf(
                content=cover_letter_content,
                job_title=job["title"], company_name=job["company"],
            )

            # Save resume record to DB
            resume_doc = {
                "is_base": False,
                "job_id": job_id,
                "base_resume_id": str(base_resume["_id"]),
                "content_json": tailored_content,
                "file_path_original_style": resume_pdf_original,
                "file_path_clean_style": resume_pdf_clean,
                "ai_model_used": tailored_content.get("_ai_metadata", {}).get("model"),
                "changes_made": tailored_content.get("changes_made", []),
                "created_at": utc_now(),
            }
            resume_result = await resumes_col.insert_one(resume_doc)

            # Save cover letter record
            cl_col = get_collection("cover_letters")
            cl_doc = {
                "job_id": job_id,
                "resume_id": str(resume_result.inserted_id),
                "content": cover_letter_content.get("full_text", ""),
                "file_path": cover_letter_pdf,
                "tone": cover_letter_content.get("_ai_metadata", {}).get("tone", "professional"),
                "created_at": utc_now(),
            }
            cl_result = await cl_col.insert_one(cl_doc)

            # ── Step 6: Apply via portal ──
            apply_result = {"success": False, "error": "No applier for this portal"}

            if portal in APPLIERS:
                applier_class = APPLIERS[portal]
                applier: BaseApplier = applier_class()
                try:
                    await applier.launch_browser()
                    logged_in = await applier.login()
                    if logged_in:
                        apply_result = await applier.apply_to_job(
                            job_url=job["url"],
                            resume_path=resume_pdf_original,
                            cover_letter_path=cover_letter_pdf,
                        )
                finally:
                    await applier.close_browser()

            # ── Step 7: Create application record ──
            app_status = "submitted" if apply_result["success"] else "failed"
            app_doc = {
                "job_id": job_id,
                "resume_id": str(resume_result.inserted_id),
                "cover_letter_id": str(cl_result.inserted_id),
                "status": app_status,
                "portal": portal,
                "apply_mode": job.get("apply_mode", "semi"),
                "confirmation_id": apply_result.get("confirmation_id"),
                "error_message": apply_result.get("error"),
                "events": [{
                    "timestamp": utc_now(),
                    "event_type": "status_change",
                    "description": f"Application {'submitted' if apply_result['success'] else 'failed'} via {portal}",
                    "metadata": apply_result,
                }],
                "job_title": job["title"],
                "company": job["company"],
                "job_url": job["url"],
                "applied_at": utc_now(),
                "updated_at": utc_now(),
            }
            app_insert = await apps_col.insert_one(app_doc)

            # Update job status
            await jobs_col.update_one(
                {"_id": ObjectId(job_id)},
                {"$set": {"status": "applied" if apply_result["success"] else "shortlisted", "updated_at": utc_now()}},
            )

            # ── Step 8: Notifications ──
            if apply_result["success"]:
                await telegram_service.notify_application_submitted(
                    title=job["title"], company=job["company"],
                    portal=portal, mode=job.get("apply_mode", "semi"),
                )
            else:
                await telegram_service.notify_application_failed(
                    title=job["title"], company=job["company"],
                    error=apply_result.get("error", "Unknown error"),
                )

            return {
                "success": apply_result["success"],
                "application_id": str(app_insert.inserted_id),
                "error": apply_result.get("error"),
            }

        except Exception as e:
            logger.error(f"Apply pipeline failed for job {job_id}: {e}")
            return {"success": False, "error": str(e)}

    async def process_auto_apply_queue(self) -> dict:
        """
        Process all jobs queued for auto-apply.
        
        Finds jobs that are shortlisted with auto apply mode
        and match_score above threshold, then applies to each.
        
        Called by the scheduler periodically.
        
        Returns:
            dict: Summary of the auto-apply run
        """
        if not settings.AUTO_APPLY_ENABLED:
            logger.debug("Auto-apply is disabled")
            return {"processed": 0, "applied": 0}

        jobs_col = get_collection("jobs")
        apps_col = get_collection("applications")

        # Count today's applications (safety limit)
        from datetime import datetime, timedelta
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0)
        today_count = await apps_col.count_documents({"applied_at": {"$gte": today_start}})

        if today_count >= 20:  # Daily safety limit
            logger.warning(f"Daily application limit reached ({today_count})")
            return {"processed": 0, "applied": 0, "reason": "daily_limit"}

        # Find eligible jobs
        query = {
            "status": {"$in": ["new", "shortlisted"]},
            "apply_mode": "auto",
            "match_score": {"$gte": settings.MIN_MATCH_SCORE_TO_APPLY},
        }
        eligible_jobs = await jobs_col.find(query).sort("match_score", -1).limit(5).to_list(5)

        results = {"processed": len(eligible_jobs), "applied": 0, "failed": 0}

        for job in eligible_jobs:
            result = await self.apply_to_job(str(job["_id"]))
            if result["success"]:
                results["applied"] += 1
            else:
                results["failed"] += 1

        return results


# ─────────────────────────────────────
# Singleton instance
# ─────────────────────────────────────
applier_manager = ApplierManager()
