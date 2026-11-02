"""
Consolidated Database Models
Adhering to Section 11 Specification & Relational Schema
"""
from app.models.user import User
from app.models.resume import Resume, ResumeAnalysis, ResumeVersion
from app.models.interview import (
    InterviewSession,
    InterviewQuestion,
    MockInterview,
    InterviewAnswer,
    InterviewSessionQuestion
)
from app.models.practice import (
    PracticeSession,
    QuestionBank,
    PracticeSubmission,
    UserQuestionHistory
)
from app.models.roadmap import CareerRoadmap, RoadmapMilestone

__all__ = [
    "User",
    "Resume",
    "ResumeAnalysis",
    "ResumeVersion",
    "InterviewSession",
    "InterviewQuestion",
    "MockInterview",
    "InterviewAnswer",
    "InterviewSessionQuestion",
    "PracticeSession",
    "QuestionBank",
    "PracticeSubmission",
    "UserQuestionHistory",
    "CareerRoadmap",
    "RoadmapMilestone"
]
