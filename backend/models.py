from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import List, Optional
from datetime import datetime


# ─────────────────────────────────────────────
# Auth Models
# ─────────────────────────────────────────────

class UserCreate(BaseModel):
    """Schema for user registration requests."""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Minimum 8 characters")

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit.")
        return v


class UserLogin(BaseModel):
    """Schema for user login requests."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Public-facing user data returned in API responses."""
    id: str
    email: str
    created_at: datetime

    class Config:
        populate_by_name = True


class TokenResponse(BaseModel):
    """JWT token response returned after register / login."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ─────────────────────────────────────────────
# Question Models
# ─────────────────────────────────────────────

class QuestionCreate(BaseModel):
    """Schema for creating a new question."""
    text: str = Field(..., min_length=5, max_length=2000, description="The question text")
    tag: Optional[str] = Field(None, max_length=100, description="Subject tag, e.g. 'math', 'physics'")

    @field_validator("text")
    @classmethod
    def text_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Question text must not be blank.")
        return v.strip()


class QuestionResponse(BaseModel):
    """
    Schema for question data returned from the API.
    Mirrors the MongoDB document shape:
      { _id, user_id, text, embedding: [], tag, similar_question_ids: [], created_at }
    """
    id: str
    user_id: str
    text: str
    embedding: List[float] = []
    tag: Optional[str] = None
    similar_question_ids: List[str] = []
    created_at: datetime

    class Config:
        populate_by_name = True
