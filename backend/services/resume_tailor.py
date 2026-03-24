"""
╔═══════════════════════════════════════════════════════════════════╗
║  JOBPILOT — Resume Tailor Service                                ║
║                                                                   ║
║  Takes your BASE resume and a job description, then uses Claude   ║
║  to produce a TAILORED version optimized for that specific job.   ║
║                                                                   ║
║  KEY PRINCIPLES:                                                  ║
║  1. Base resume is NEVER modified — it's the source of truth     ║
║  2. All experience bullets are REAL — AI only rewords, never     ║
║     fabricates achievements or skills you don't have              ║
║  3. Two output versions: original-style + clean-template          ║
║  4. Changes are tracked so you can see exactly what was altered   ║
║                                                                   ║
║  WHAT THE AI DOES:                                                ║
║  - Rewords professional summary to match the job                 ║
║  - Reorders skills to prioritize job-relevant ones               ║
║  - Adjusts experience bullet points to emphasize relevant work    ║
║  - Adds job-relevant keywords naturally (ATS optimization)       ║
║                                                                   ║
║  WHAT THE AI DOES NOT DO:                                         ║
║  - Invent fake experience or projects                            ║
║  - Add skills the candidate doesn't have                         ║
║  - Change job titles, dates, or factual information              ║
║  - Fabricate metrics or achievements                             ║
╚═══════════════════════════════════════════════════════════════════╝
"""

import json
from typing import Optional
from services.ai_service import ai_service
from utils.logger import logger


class ResumeTailorService:
    """
    Tailors resumes for specific job descriptions using Claude AI.
    
    Flow:
    1. Receive base resume text + job description
    2. Claude analyzes the job requirements
    3. Claude rewrites the resume sections to better match
    4. Returns structured JSON with tailored content
    5. PDF generator creates the final documents
    """

    TAILOR_SYSTEM_PROMPT = """You are an expert resume writer and career coach. Your job is to 
tailor an existing resume to better match a specific job description.

CRITICAL RULES — YOU MUST FOLLOW THESE:
1. NEVER invent experience, projects, skills, or achievements the candidate doesn't have
2. NEVER change job titles, company names, dates, or educational qualifications
3. NEVER add skills not evident from the original resume
4. NEVER fabricate metrics or numbers — only use what exists in the original
5. You CAN reword bullet points to emphasize relevant aspects
6. You CAN reorder skills and bullet points to prioritize relevant ones
7. You CAN adjust the professional summary to target the specific role
8. You CAN add job-relevant keywords IF the candidate demonstrably has that skill

Your goal is to make the resume TRUTHFUL but OPTIMIZED for this specific job.

Respond ONLY with valid JSON in this exact format:
{
    "professional_summary": "2-3 sentence tailored summary",
    "skills_reordered": ["skill1", "skill2", "..."],
    "experience": [
        {
            "company": "Company Name",
            "role": "Original Job Title",
            "duration": "Original Duration",
            "bullets": [
                "Reworded bullet point 1",
                "Reworded bullet point 2"
            ]
        }
    ],
    "education": {
        "institution": "Original Institution",
        "degree": "Original Degree",
        "details": "Original Details"
    },
    "achievements": ["achievement1", "achievement2"],
    "changes_made": [
        "Description of change 1",
        "Description of change 2"
    ],
    "ats_keywords_added": ["keyword1", "keyword2"]
}"""

    async def tailor_resume(
        self,
        base_resume_text: str,
        job_title: str,
        job_description: str,
        job_skills: list,
        company_name: str,
    ) -> dict:
        """
        Generate a tailored version of the resume for a specific job.
        
        Args:
            base_resume_text: Full text of the original/base resume
            job_title: Title of the target job
            job_description: Full job description
            job_skills: Skills mentioned in the job posting
            company_name: Company name (for personalizing the summary)
        
        Returns:
            dict: Structured tailored resume content (see JSON format above)
                  Also includes AI metadata (tokens used, model, etc.)
        """
        prompt = f"""Tailor this resume for the following job posting.

=== CANDIDATE PROFILE ===
{ai_service.profile if ai_service.profile else 'See resume below'}

=== TARGET JOB ===
Title: {job_title}
Company: {company_name}
Required Skills: {', '.join(job_skills) if job_skills else 'See description'}
Job Description:
{job_description[:5000]}

=== ORIGINAL RESUME ===
{base_resume_text[:6000]}

Tailor the resume following the rules. Respond with JSON only."""

        try:
            result = await ai_service.chat_json(
                user_message=prompt,
                system_prompt=self.TAILOR_SYSTEM_PROMPT,
                max_tokens=4096,
                temperature=0.3,
            )

            tailored = result["data"]

            # Attach AI metadata for tracking
            tailored["_ai_metadata"] = {
                "model": result["model"],
                "input_tokens": result["input_tokens"],
                "output_tokens": result["output_tokens"],
            }

            logger.info(
                f"Resume tailored for '{job_title}' at {company_name}. "
                f"Changes: {len(tailored.get('changes_made', []))} modifications."
            )

            return tailored

        except Exception as e:
            logger.error(f"Resume tailoring failed for '{job_title}': {e}")
            raise

    async def extract_resume_text(self, resume_content: dict) -> str:
        """
        Convert structured resume JSON back to plain text.
        
        Used when we need a text representation of a tailored resume
        (e.g., for pasting into job portal text fields).
        
        Args:
            resume_content: Structured resume dict from tailor_resume()
        
        Returns:
            str: Plain text version of the resume
        """
        sections = []

        # Professional Summary
        if resume_content.get("professional_summary"):
            sections.append(f"PROFESSIONAL SUMMARY\n{resume_content['professional_summary']}")

        # Skills
        if resume_content.get("skills_reordered"):
            skills_text = ", ".join(resume_content["skills_reordered"])
            sections.append(f"SKILLS\n{skills_text}")

        # Experience
        if resume_content.get("experience"):
            exp_lines = ["EXPERIENCE"]
            for exp in resume_content["experience"]:
                exp_lines.append(f"\n{exp.get('role', '')} | {exp.get('company', '')} | {exp.get('duration', '')}")
                for bullet in exp.get("bullets", []):
                    exp_lines.append(f"  • {bullet}")
            sections.append("\n".join(exp_lines))

        # Education
        if resume_content.get("education"):
            edu = resume_content["education"]
            sections.append(
                f"EDUCATION\n{edu.get('degree', '')} | {edu.get('institution', '')} | {edu.get('details', '')}"
            )

        # Achievements
        if resume_content.get("achievements"):
            ach_lines = ["ACHIEVEMENTS"]
            for ach in resume_content["achievements"]:
                ach_lines.append(f"  • {ach}")
            sections.append("\n".join(ach_lines))

        return "\n\n".join(sections)


# ─────────────────────────────────────
# Singleton instance
# ─────────────────────────────────────
resume_tailor = ResumeTailorService()
