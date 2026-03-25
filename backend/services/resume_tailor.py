"""
JOBPILOT — Resume Tailor Service (LaTeX-based)

Takes the user's LaTeX resume and a job description, then uses AI
to modify the LaTeX content (reword bullets, reorder skills, adjust summary)
while preserving all LaTeX formatting and commands.
"""

from services.ai_service import ai_service
from utils.logger import logger


class ResumeTailorService:

    SYSTEM_PROMPT = """You are an expert resume writer. You will receive a LaTeX resume and a job description.

Your task: Modify the LaTeX resume content to better match the job. Return the COMPLETE modified LaTeX file.

RULES:
1. NEVER invent experience, projects, skills, or achievements
2. NEVER change job titles, company names, dates, or education
3. NEVER break LaTeX syntax — the output must compile with pdflatex
4. You CAN reword bullet points to emphasize job-relevant aspects
5. You CAN reorder skills to prioritize relevant ones first
6. You CAN adjust wording to include job-relevant keywords naturally
7. Keep ALL LaTeX commands, packages, and formatting exactly as-is
8. Only modify TEXT CONTENT inside the LaTeX structure

After the complete LaTeX, add a line "%%CHANGES%%" followed by a brief list of what you changed, one per line starting with "- "."""

    async def tailor_resume(
        self,
        latex_source: str,
        job_title: str,
        job_description: str,
        job_skills: list,
        company_name: str,
    ) -> dict:
        prompt = f"""Modify this LaTeX resume for the following job.

=== TARGET JOB ===
Title: {job_title}
Company: {company_name}
Skills: {', '.join(job_skills) if job_skills else 'See description'}
Description:
{job_description[:3000] if job_description else 'Not available'}

=== LATEX RESUME (modify this and return the complete file) ===
{latex_source}"""

        result = await ai_service.chat(
            user_message=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            max_tokens=8192,
        )

        content = result["content"]

        # Split LaTeX from changes list
        latex_out = content
        changes = []

        if "%%CHANGES%%" in content:
            parts = content.split("%%CHANGES%%", 1)
            latex_out = parts[0].strip()
            changes = [l.strip().lstrip("- ") for l in parts[1].strip().split("\n") if l.strip().startswith("- ")]

        # Extract LaTeX if wrapped in code fences
        if "\\documentclass" in latex_out:
            start = latex_out.find("\\documentclass")
            end = latex_out.rfind("\\end{document}")
            if end > start:
                latex_out = latex_out[start:end + len("\\end{document}")]

        if "\\documentclass" not in latex_out:
            raise RuntimeError("AI response did not contain valid LaTeX")

        logger.info(f"Resume tailored for '{job_title}' at {company_name}. Changes: {len(changes)}")

        return {
            "latex_source": latex_out,
            "changes_made": changes,
        }


resume_tailor = ResumeTailorService()
