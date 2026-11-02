"""
Pydantic Schemas for Virtual AI Interviewer & Career Coach
"""
from app.schemas.user import (
    UserRegister,
    UserLogin,
    UserProfileUpdate,
    Token,
    UserResponse,
    AIPreferenceUpdate
)
from app.schemas.resume import (
    ResumeAnalysisResponse,
    ResumeResponse,
    ResumeGenerateRequest,
    ResumeExtractedDataUpdate,
    ResumeCorrectionActionRequest,
    RoleOptimizeRequest,
    RoleOptimizeResponse,
    JobMatchRequest,
    JobMatchResponse
)
from app.schemas.interview import (
    InterviewStartRequest,
    InterviewAnswerRequest,
    InterviewSessionResponse,
    InterviewQuestionResponse,
    AudioTranscribeResponse
)
from app.schemas.practice import (
    QuestionBankItem,
    PracticeSubmitRequest,
    PracticeEvaluationResponse,
    StartPracticeSessionRequest,
    PracticeSessionStateResponse,
    PracticeAnswerSubmitRequest,
    PracticeSessionAnswerResponse,
    ExecuteCodeRequest,
    PracticeMetadataResponse
)
from app.schemas.roadmap import (
    RoadmapGenerateRequest,
    RoadmapResponse,
    TaskToggleRequest,
    MilestoneToggleRequest
)
