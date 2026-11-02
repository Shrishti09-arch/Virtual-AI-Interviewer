from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserRegister, UserLogin, UserProfileUpdate, Token, UserResponse, AIPreferenceUpdate
from app.services.auth_service import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
    security
)
from app.core.security import validate_password_strength, revoke_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=Token)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    # 1. Enforce strict password policy
    is_valid_pw, pw_msg = validate_password_strength(user_in.password)
    if not is_valid_pw:
        raise HTTPException(status_code=400, detail=pw_msg)

    # 2. Check existing account
    existing = db.query(User).filter(User.email == user_in.email.strip().lower()).first()
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email already exists")

    new_user = User(
        email=user_in.email.strip().lower(),
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name.strip(),
        role_target=user_in.role_target,
        experience_level=user_in.experience_level,
        skills=["JavaScript", "React", "Python"]
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token(data={"sub": str(new_user.id)})
    return Token(
        access_token=token,
        token_type="bearer",
        user_id=new_user.id,
        email=new_user.email,
        full_name=new_user.full_name
    )

@router.post("/login", response_model=Token)
def login(login_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_in.email.strip().lower()).first()
    if not user or not verify_password(login_in.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    token = create_access_token(data={"sub": str(user.id)})
    return Token(
        access_token=token,
        token_type="bearer",
        user_id=user.id,
        email=user.email,
        full_name=user.full_name
    )

@router.post("/logout")
def logout(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    current_user: User = Depends(get_current_user)
):
    """
    Secure Session Management:
    Revokes the current JWT access token, adding it to the revocation blacklist
    so it cannot be reused even before natural expiration.
    """
    if credentials and credentials.credentials:
        revoke_token(credentials.credentials)
    return {
        "status": "success",
        "detail": "Session token revoked successfully. Logged out."
    }

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/profile", response_model=UserResponse)
def update_profile(
    profile_in: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if profile_in.full_name is not None:
        current_user.full_name = profile_in.full_name.strip()
    if profile_in.role_target is not None:
        current_user.role_target = profile_in.role_target.strip()
    if profile_in.experience_level is not None:
        current_user.experience_level = profile_in.experience_level
    if profile_in.bio is not None:
        current_user.bio = profile_in.bio
    if profile_in.skills is not None:
        current_user.skills = profile_in.skills

    db.commit()
    db.refresh(current_user)
    return current_user

@router.put("/ai-preferences", response_model=UserResponse)
def update_ai_preferences(
    prefs: AIPreferenceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    current_user.llm_preference = prefs.llm_preference
    if prefs.groq_api_key is not None:
        current_user.groq_api_key = prefs.groq_api_key.strip()
    if prefs.ollama_endpoint is not None:
        current_user.ollama_endpoint = prefs.ollama_endpoint.strip()

    db.commit()
    db.refresh(current_user)
    return current_user
