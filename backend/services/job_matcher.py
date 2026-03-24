"""
╔═══════════════════════════════════════════════════════════════════╗
║  JOBPILOT — Job Matcher Service                                  ║
║                                                                   ║
║  Uses Claude AI to score how well a job matches your profile.     ║
║                                                                   ║
║  SCORING CRITERIA (weighted):                                     ║
║    - Skills match (35%): How many required skills you have        ║
║    - Experience fit (25%): Does your YOE fall in range?           ║
║    - Role alignment (20%): Is the title/role what you want?       ║
║    - Location match (10%): Is it in your preferred locations?     ║
║    - Company/culture (10%): Company size, industry fit            ║
║                                                                   ║
║  OUTPUT: Score 0-100 + human-readable reasoning                   ║
║                                                                   ║
║  USAGE:                                                           ║
║    from services.job_matcher import job_matcher                    ║
║    score, reasoning = await job_matcher.score_job(job, profile)   ║
╚═══════════════════════════════════════════════════════════════════╝
"""

from typing import Tuple, Optional
from services.ai_service import ai_service
from utils.logger import logger


class JobMatcherService:
    """
    Scores jobs against the user's profile using Claude AI.
    
    The scoring is done in a single Claude API call that analyzes
    the job description against the user's resume and preferences,
    returning both a numeric score and reasoning.
    """

    # System prompt that instructs Claude how to score jobs
    SCORING_SYSTEM_PROMPT = """You are a job matching expert. Your task is to analyze a job posting 
against a candidate's profile and provide a match score.

Score the match from 0 to 100 based on these weighted criteria:
- Skills Match (35%): How many of the job's required skills does the candidate have?
- Experience Fit (25%): Does the candidate's years of experience match the requirement?
- Role Alignment (20%): Is this the type of role the candidate is targeting?
- Location Match (10%): Is the job in one of the candidate's preferred locations?
- Growth Potential (10%): Does this role offer growth aligned with candidate's career direction?

SCORING GUIDE:
- 90-100: Perfect match — candidate exceeds most requirements
- 75-89: Strong match — candidate meets most requirements
- 60-74: Good match — candidate meets core requirements, gaps are minor
- 40-59: Moderate match — some alignment but significant gaps
- 20-39: Weak match — major misalignments
- 0-19: Poor match — wrong role/domain entirely

Be honest and precise. Don't inflate scores.

Respond ONLY with valid JSON in this exact format:
{
    "score": <integer 0-100>,
    "reasoning": "<2-3 sentence explanation>",
    "matching_skills": ["skill1", "skill2"],
    "missing_skills": ["skill1", "skill2"],
    "experience_fit": "perfect|good|stretch|overqualified|underqualified",
    "key_strengths": ["strength1", "strength2"],
    "concerns": ["concern1", "concern2"]
}"""

    async def score_job(
        self,
        job_title: str,
        job_description: str,
        job_skills: list,
        job_location: str,
        job_experience: str,
        resume_text: str,
        user_target_roles: list,
        user_target_locations: list,
        user_skills: list,
        user_experience_years: float,
    ) -> dict:
        """
        Score a job against the user's profile.
        
        This is the main method — it constructs a prompt with the job
        and profile data, sends it to Claude, and returns the parsed score.
        
        Args:
            job_title: Title of the job posting
            job_description: Full job description text
            job_skills: Skills mentioned in the job posting
            job_location: Job location
            job_experience: Experience requirement text
            resume_text: User's full resume text
            user_target_roles: Roles the user is targeting
            user_target_locations: Preferred locations
            user_skills: User's listed skills
            user_experience_years: User's total years of experience
        
        Returns:
            dict with keys: score, reasoning, matching_skills, missing_skills,
                           experience_fit, key_strengths, concerns
        """
        # Build the prompt with all context
        prompt = f"""Analyze this job posting against the candidate's profile:

=== JOB POSTING ===
Title: {job_title}
Location: {job_location or 'Not specified'}
Experience Required: {job_experience or 'Not specified'}
Required Skills: {', '.join(job_skills) if job_skills else 'Not specified'}
Description:
{job_description[:4000] if job_description else 'No description available'}

=== CANDIDATE PROFILE ===
Experience: {user_experience_years} years
Target Roles: {', '.join(user_target_roles)}
Preferred Locations: {', '.join(user_target_locations)}
Skills: {', '.join(user_skills)}

Resume Summary:
{resume_text[:3000] if resume_text else 'No resume text available'}

Score this match and respond with JSON only."""

        try:
            result = await ai_service.chat_json(
                user_message=prompt,
                system_prompt=self.SCORING_SYSTEM_PROMPT,
                max_tokens=1024,
                temperature=0.2,  # Low temperature for consistent scoring
            )

            score_data = result["data"]

            # Validate score is within range
            score = max(0, min(100, int(score_data.get("score", 0))))
            score_data["score"] = score

            logger.info(
                f"Job scored: '{job_title}' → {score}/100 "
                f"({score_data.get('experience_fit', 'unknown')} experience fit)"
            )

            return score_data

        except Exception as e:
            logger.error(f"Job scoring failed for '{job_title}': {e}")
            # Return a default score on failure so the pipeline doesn't break
            return {
                "score": 50,
                "reasoning": f"Auto-scoring failed: {str(e)}. Manual review recommended.",
                "matching_skills": [],
                "missing_skills": [],
                "experience_fit": "unknown",
                "key_strengths": [],
                "concerns": ["Scoring failed — review manually"],
            }

    async def quick_score(
        self,
        job_title: str,
        job_skills: list,
        job_location: str,
        user_skills: list,
        user_target_locations: list,
    ) -> int:
        """
        Fast, heuristic-based scoring WITHOUT using the AI API.
        
        Used for initial filtering of large batches of jobs before
        spending API tokens on detailed scoring. This is a simple
        keyword-overlap approach.
        
        Args:
            job_title: Job title
            job_skills: Skills from job posting
            job_location: Job location
            user_skills: User's skills
            user_target_locations: User's preferred locations
        
        Returns:
            int: Quick score 0-100 (rough estimate)
        """
        score = 0

        # ── Skills overlap (up to 50 points) ──
        if job_skills and user_skills:
            job_skills_lower = {s.lower() for s in job_skills}
            user_skills_lower = {s.lower() for s in user_skills}
            overlap = job_skills_lower & user_skills_lower
            if job_skills_lower:
                skill_ratio = len(overlap) / len(job_skills_lower)
                score += int(skill_ratio * 50)

        # ── Location match (up to 20 points) ──
        if job_location and user_target_locations:
            location_lower = job_location.lower()
            for loc in user_target_locations:
                if loc.lower() in location_lower or location_lower in loc.lower():
                    score += 20
                    break
            # "Remote" is always a match
            if "remote" in location_lower:
                score += 20

        # ── Title relevance (up to 30 points) ──
        title_lower = job_title.lower() if job_title else ""
        relevant_keywords = [
            "backend", "full stack", "fullstack", "sde", "software engineer",
            "software developer", "backend developer", "java", "node",
            "python", "spring boot"
        ]
        keyword_hits = sum(1 for kw in relevant_keywords if kw in title_lower)
        score += min(30, keyword_hits * 10)

        return min(100, score)


# ─────────────────────────────────────
# Singleton instance
# ─────────────────────────────────────
job_matcher = JobMatcherService()
