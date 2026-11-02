import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, event
from app.database import Base

class User(Base):
    """
    Users table adhering to Section 11 Database specification:
    - id
    - name (with backward-compatible full_name sync)
    - email
    - password_hash (with backward-compatible hashed_password sync)
    - created_at
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=True)
    full_name = Column(String(255), nullable=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=True)
    hashed_password = Column(String(255), nullable=True)
    role_target = Column(String(255), default="Full Stack Software Engineer")
    experience_level = Column(String(50), default="1-3 years")
    bio = Column(Text, nullable=True)
    skills = Column(JSON, default=list)
    llm_preference = Column(String(50), default="smart_fallback")
    groq_api_key = Column(String(255), nullable=True)
    ollama_endpoint = Column(String(255), default="http://localhost:11434")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def __init__(self, **kwargs):
        if "full_name" in kwargs and "name" not in kwargs:
            kwargs["name"] = kwargs["full_name"]
        elif "name" in kwargs and "full_name" not in kwargs:
            kwargs["full_name"] = kwargs["name"]

        if "hashed_password" in kwargs and "password_hash" not in kwargs:
            kwargs["password_hash"] = kwargs["hashed_password"]
        elif "password_hash" in kwargs and "hashed_password" not in kwargs:
            kwargs["hashed_password"] = kwargs["password_hash"]
        super().__init__(**kwargs)


@event.listens_for(User, "before_insert")
def sync_user_fields_insert(mapper, connection, target):
    if target.name and not target.full_name:
        target.full_name = target.name
    elif target.full_name and not target.name:
        target.name = target.full_name

    if target.password_hash and not target.hashed_password:
        target.hashed_password = target.password_hash
    elif target.hashed_password and not target.password_hash:
        target.password_hash = target.hashed_password


@event.listens_for(User, "before_update")
def sync_user_fields_update(mapper, connection, target):
    if target.name and not target.full_name:
        target.full_name = target.name
    elif target.full_name and not target.name:
        target.name = target.full_name

    if target.password_hash and not target.hashed_password:
        target.hashed_password = target.password_hash
    elif target.hashed_password and not target.password_hash:
        target.password_hash = target.hashed_password
