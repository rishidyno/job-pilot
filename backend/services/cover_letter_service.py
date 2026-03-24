"""
╔═══════════════════════════════════════════════════════════════════╗
║  JOBPILOT — Cover Letter Service                                 ║
║                                                                   ║
║  Generates personalized cover letters using Claude AI.            ║
║  Each cover letter is tailored to a specific job posting          ║
║  and references the candidate's actual experience.                ║
║                                                                   ║
║  USAGE:                                                           ║
║    from services.cover_letter_service import cover_letter_service  ║
║    letter = await cover_letter_service.generate(...)              ║
╚═══════════════════════════════════════════════════════════════════╝
"""

from typing import Optional
from services.ai_service import ai_service
from utils.logger import logger


class CoverLetterService:
    """
    Generates cover letters tailored to specific job postings.
    
    The cover letter draws from:
    - The candidate's resume (real experience and skills)
    - The job description (what the company is looking for)
    - The company name (for personalization)
    """

    COVER_LETTER_SYSTEM_PROMPT = """You are an expert cover letter writer. Write a compelling, 
personalized cover letter for a job application.

RULES:
1. Keep it to 3-4 paragraphs (250-350 words)
2. Be genuine and specific — reference actual experience from the resume
3. Don't be generic — mention the company name and specific job requirements
4. Show enthusiasm without being over-the-top
5. Highlight 2-3 specific achievements that align with the job
6. NEVER fabricate experience or skills not in the resume
7. End with a clear call-to-action (interview request)
8. Use professional but warm tone

STRUCTURE:
- Paragraph 1: Hook — why you're excited about THIS role at THIS company
- Paragraph 2: Your most relevant experience and achievements
- Paragraph 3: Additional skills/experience that add value
- Paragraph 4: Closing — enthusiasm + call to action

Respond ONLY with valid JSON:
{
    "subject_line": "Application for [Role] - [Your Name]",
    "greeting": "Dear Hiring Manager,",
    "body": "Full cover letter text with proper paragraph breaks (use \\n\\n for paragraph separation)",
    "closing": "Best regards,\\n[Name]",
    "full_text": "Complete cover letter from greeting to closing"
}"""

    async def generate(
        self,
        resume_text: str,
        job_title: str,
        job_description: str,
        company_name: str,
        candidate_name: str = "Rishi Raj",
        tone: str = "professional",
    ) -> dict:
        """
        Generate a tailored cover letter.
        
        Args:
            resume_text: Candidate's resume text (base or tailored)
            job_title: Title of the target job
            job_description: Full job description
            company_name: Name of the hiring company
            candidate_name: Candidate's full name
            tone: Writing tone: "professional", "enthusiastic", "concise"
        
        Returns:
            dict: Cover letter content with subject_line, greeting, body, closing, full_text
        """
        # Adjust tone instruction
        tone_instruction = {
            "professional": "Use a professional, confident tone.",
            "enthusiastic": "Use an enthusiastic, energetic tone that shows genuine excitement.",
            "concise": "Keep it very concise and to-the-point. Maximum 200 words.",
        }.get(tone, "Use a professional, confident tone.")

        prompt = f"""Write a cover letter for this job application.

Candidate Name: {candidate_name}
Tone: {tone_instruction}

=== JOB POSTING ===
Title: {job_title}
Company: {company_name}
Description:
{job_description[:4000]}

=== CANDIDATE RESUME ===
{resume_text[:4000]}

Generate the cover letter as JSON."""

        try:
            result = await ai_service.chat_json(
                user_message=prompt,
                system_prompt=self.COVER_LETTER_SYSTEM_PROMPT,
                max_tokens=2048,
                temperature=0.5,  # Slightly higher temp for more natural writing
            )

            letter_data = result["data"]

            # Attach metadata
            letter_data["_ai_metadata"] = {
                "model": result["model"],
                "input_tokens": result["input_tokens"],
                "output_tokens": result["output_tokens"],
                "tone": tone,
            }

            logger.info(f"Cover letter generated for '{job_title}' at {company_name}")
            return letter_data

        except Exception as e:
            logger.error(f"Cover letter generation failed for '{job_title}': {e}")
            raise


# ─────────────────────────────────────
# Singleton instance
# ─────────────────────────────────────
cover_letter_service = CoverLetterService()
