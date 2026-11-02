from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class UserRegister(BaseModel):
    email: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=1, max_length=255)
    role_target: Optional[str] = "Full Stack Software Engineer"
    experience_level: Optional[str] = "1-3 years"

class UserLogin(BaseModel):
    email: str
    password: str

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    role_target: Optional[str] = None
    experience_level: Optional[str] = None
    bio: Optional[str] = None
    skills: Optional[List[str]] = None

class AIPreferenceUpdate(BaseModel):
    llm_preference: str # smart_fallback, groq, ollama, lmstudio, huggingface
    groq_api_key: Optional[str] = None
    ollama_endpoint: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    email: str
    full_name: str

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role_target: Optional[str] = None
    experience_level: Optional[str] = None
    bio: Optional[str] = None
    skills: List[str] = []
    llm_preference: str
    created_at: datetime

    class Config:
        from_attributes = True
