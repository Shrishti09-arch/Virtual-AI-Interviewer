"""
Resume Processing and Role-Based AI Resume Builder Service
Provides document text extraction (PDF/DOCX), structured parsing,
truthful AI role optimization (12 supported roles), and ATS-friendly PDF/DOCX generation.
"""
from typing import Dict, Any, List, Optional
from app.services.resume_service import ResumeService

# Canonical singleton instance
resume_service = ResumeService

__all__ = ["ResumeService", "resume_service"]
