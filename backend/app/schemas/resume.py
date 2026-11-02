from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class ResumeAnalyzeRequest(BaseModel):
    raw_text: Optional[str] = None
    target_role: str = "Full Stack Software Engineer"
    job_description: Optional[str] = None

class SectionScore(BaseModel):
    name: str
    score: float # 0-100
    status: str # "Good", "Needs Improvement", "Missing"
    feedback: str

# Extracted structured resume sections for user review & editing
class ExtractedEducationItem(BaseModel):
    institution: str
    degree: str
    year: Optional[str] = ""
    grade: Optional[str] = ""

class ExtractedExperienceItem(BaseModel):
    company: str
    role: str
    duration: str
    location: Optional[str] = ""
    highlights: List[str] = []

class ExtractedInternshipItem(BaseModel):
    company: str
    role: str
    duration: str
    highlights: List[str] = []

class ExtractedProjectItem(BaseModel):
    name: str
    technologies: List[str] = []
    description: str = ""
    link: Optional[str] = ""

class ExtractedResumeData(BaseModel):
    full_name: str = ""
    email: str = ""
    phone: str = ""
    location: Optional[str] = ""
    linkedin: Optional[str] = ""
    github: Optional[str] = ""
    summary: Optional[str] = ""
    education: List[ExtractedEducationItem] = []
    technical_skills: Dict[str, List[str]] = {}
    work_experience: List[ExtractedExperienceItem] = []
    internships: List[ExtractedInternshipItem] = []
    projects: List[ExtractedProjectItem] = []
    certifications: List[str] = []
    achievements: List[str] = []

class ResumeExtractedDataUpdate(BaseModel):
    extracted_data: ExtractedResumeData

class GrammarErrorItem(BaseModel):
    snippet: str
    issue: str
    suggestion: str

class WeakSentenceItem(BaseModel):
    original: str
    issue: str
    suggestion: str

class ResumeCorrectionItem(BaseModel):
    id: str
    category: str # "Action Verb", "Grammar", "Sentence Construction", "Professional Tone", "Incomplete Sentence"
    original: str
    corrected: str
    explanation: str
    status: str = "pending" # "pending", "accepted", "rejected"

class ResumeCorrectionActionRequest(BaseModel):
    action: str = "accept" # "accept" or "reject"

class ResumeAnalysisResponse(BaseModel):
    id: int
    resume_id: int
    target_role: str
    overall_ats_score: float
    keyword_match_score: float
    structure_score: float
    impact_score: float
    readability_score: float = 75.0
    section_scores: Dict[str, Any] = {}
    matched_skills: List[str] = []
    missing_skills: List[str] = []
    missing_keywords: List[str] = []
    grammar_errors: List[Dict[str, Any]] = []
    weak_sentences: List[Dict[str, Any]] = []
    formatting_issues: List[str] = []
    action_verb_suggestions: List[str] = []
    improvement_recommendations: List[str] = []
    corrections: List[Dict[str, Any]] = []
    section_breakdown: Dict[str, Any] = {}
    readability_metrics: Dict[str, Any] = {}
    extracted_data: Optional[Dict[str, Any]] = None
    disclaimer: str = (
        "Notice: Estimated ATS compatibility scores are heuristic benchmarks based on standard parsing algorithms, "
        "structural completeness, and keyword weighting. They are not guaranteed results for any specific proprietary commercial ATS."
    )
    detailed_feedback: str = ""
    created_at: datetime

    class Config:
        from_attributes = True

class ResumeWorkExperience(BaseModel):
    company: str
    role: str
    duration: str
    highlights: List[str]

class ResumeEducation(BaseModel):
    institution: str
    degree: str
    year: str
    grade: Optional[str] = None

class ResumeProject(BaseModel):
    name: str
    technologies: List[str]
    description: str
    link: Optional[str] = None

class ResumeGenerateRequest(BaseModel):
    full_name: str
    email: str
    phone: str
    location: str
    linkedin: Optional[str] = None
    github: Optional[str] = None
    target_role: str
    experience_level: Optional[str] = "Mid-Level"
    professional_summary: str
    skills: Dict[str, List[str]] # e.g. {"Languages": ["Python", "TS"], "Frameworks": ["React", "FastAPI"]}
    experience: List[ResumeWorkExperience] = []
    education: List[ResumeEducation] = []
    projects: List[ResumeProject] = []
    internships: Optional[List[ResumeWorkExperience]] = []
    certifications: Optional[List[str]] = []
    achievements: Optional[List[str]] = []
    template_style: Optional[str] = "modern" # "modern", "classic", "minimalist"
    section_order: Optional[List[str]] = None

class RoleOptimizeRequest(BaseModel):
    target_role: str
    experience_level: str = "Mid-Level" # "Student / Intern", "Entry Level", "Mid-Level", "Senior", "Lead"
    full_name: Optional[str] = "Candidate"
    professional_summary: Optional[str] = ""
    skills: Optional[Dict[str, List[str]]] = {}
    experience: Optional[List[ResumeWorkExperience]] = []
    education: Optional[List[ResumeEducation]] = []
    projects: Optional[List[ResumeProject]] = []
    internships: Optional[List[ResumeWorkExperience]] = []
    certifications: Optional[List[str]] = []
    achievements: Optional[List[str]] = []
    job_description: Optional[str] = None

class RoleOptimizeResponse(BaseModel):
    target_role: str
    experience_level: str
    optimized_summary: str
    recommended_skills: Dict[str, List[str]]
    missing_keywords: List[str]
    matched_keywords: List[str]
    optimized_projects: List[ResumeProject]
    optimized_experience: List[ResumeWorkExperience]
    recommended_section_order: List[str]
    estimated_ats_score: float
    disclaimer: str = (
        "Notice: Estimated ATS compatibility scores are heuristic benchmarks based on standard parsing algorithms, "
        "structural completeness, and keyword weighting. They are not guaranteed results for any specific proprietary commercial ATS."
    )
    tips: List[str]

class RelevantExperienceItem(BaseModel):
    resume_snippet: str
    matched_jd_requirement: str
    relevance_score: float # 0-100

class TechnicalSkillGap(BaseModel):
    category: str
    missing_skills: List[str]
    impact: str # "Critical", "Important", "Nice-to-Have"
    recommendation: str

class JobMatchRequest(BaseModel):
    resume_id: Optional[int] = None
    resume_text: Optional[str] = None
    job_description: str
    target_role: Optional[str] = "Software Engineer"

class JobMatchResponse(BaseModel):
    keyword_match_percentage: float
    overall_fit_score: float
    matching_skills: List[str]
    missing_skills: List[str]
    relevant_experience: List[RelevantExperienceItem]
    technical_skill_gaps: List[TechnicalSkillGap]
    recommendations: List[str]
    summary_verdict: str
    top_keywords_in_jd: List[str]
    candidate_strengths: List[str]
    disclaimer: str = (
        "Notice: Job description match percentages are computed using vector cosine similarity and keyword taxonomy overlap. "
        "They simulate automated ATS filtering and should be used as preparation benchmarks rather than hiring guarantees."
    )

class ResumeResponse(BaseModel):
    id: int
    title: str
    target_role: Optional[str]
    file_name: Optional[str]
    parsed_data: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True
