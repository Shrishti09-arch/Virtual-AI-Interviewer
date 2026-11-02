"""
Dedicated ATS (Applicant Tracking System) Scoring & JD Matcher Service
Evaluates resumes for keyword density, structural parsing compliance, role-specific competency match,
and job description alignment with zero hallucination.
"""
from typing import Dict, Any, List, Optional
from app.services.resume_service import ResumeService


class ATSService:
    """
    Enterprise-grade ATS compliance and scoring engine.
    Calculates detailed ATS metrics, missing keywords, section scores, and job description match.
    """

    @classmethod
    def audit_resume(
        cls,
        resume_text: str,
        target_role: str,
        job_description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform a comprehensive ATS audit on raw resume text.
        Returns:
            overall_score: int (0-100)
            breakdown: sub-scores for keywords, experience, education, formatting
            matched_keywords: list of found role/industry terms
            missing_keywords: critical high-frequency terms absent
            structural_issues: formatting and readability warnings
            actionable_recommendations: concrete tips for score maximization
        """
        return ResumeService.analyze_resume(
            resume_text=resume_text,
            target_role=target_role,
            job_description=job_description
        )

    @classmethod
    def match_job_description(
        cls,
        resume_text: str,
        job_description: str,
        target_role: str = "Software Engineer"
    ) -> Dict[str, Any]:
        """
        Compare resume against specific job description.
        Returns matched skills, missing skills, keyword match percentage,
        experience alignment, and gap analysis.
        """
        return ResumeService.match_job_description(
            resume_text=resume_text,
            job_description=job_description,
            target_role=target_role
        )

    @classmethod
    def extract_structured_data(cls, resume_text: str) -> Dict[str, Any]:
        """
        Extract clean structured data (contact, education, skills, experience, projects)
        from plain resume text.
        """
        return ResumeService.extract_structured_resume_data(resume_text)


ats_service = ATSService()

__all__ = ["ATSService", "ats_service"]
