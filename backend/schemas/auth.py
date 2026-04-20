"""Pydantic schemas for Authentication endpoints."""

from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime


# ── Request Schemas ───────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: Optional[str] = "analyst"

    @field_validator("role")
    @classmethod
    def validate_role(cls, v):
        allowed = {"admin", "analyst", "viewer"}
        if v not in allowed:
            raise ValueError(f"Role must be one of: {allowed}")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v


class UserLogin(BaseModel):
    username: str
    password: str


# ── Response Schemas ──────────────────────────────────────────────────────────

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class MessageResponse(BaseModel):
    message: str
    success: bool = True
