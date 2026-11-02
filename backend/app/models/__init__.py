from app.models.user import User
from app.models.resume import Resume, ResumeVersion, ResumeAnalysis
from app.models.practice import (
    InterviewQuestion,
    QuestionBank,
    PracticeSession,
    PracticeSubmission,
    UserQuestionHistory
)
from app.models.interview import (
    MockInterview,
    InterviewAnswer,
    InterviewSession,
    InterviewQuestion as InterviewSessionQuestion
)
from app.models.roadmap import (
    Roadmap,
    CareerRoadmap,
    RoadmapMilestone
)

__all__ = [
    # 8 Primary Tables Specified in Section 11 Database
    "User",
    "Resume",
    "ResumeVersion",
    "InterviewQuestion",
    "PracticeSession",
    "MockInterview",
    "InterviewAnswer",
    "Roadmap",

    # Extended application models
    "QuestionBank",
    "ResumeAnalysis",
    "InterviewSession",
    "InterviewSessionQuestion",
    "PracticeSubmission",
    "UserQuestionHistory",
    "CareerRoadmap",
    "RoadmapMilestone",
]
