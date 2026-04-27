"""Auth Router — /api/v1/auth"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from limiter_config import limiter
from sqlalchemy.orm import Session

from database import get_db
from schemas.auth import UserRegister, UserLogin, UserOut, TokenResponse, MessageResponse
from services.auth_service import (
    authenticate_user, create_user, create_access_token, get_user_by_username
)
from middleware.auth_middleware import get_current_user
from models.user import User

router = APIRouter()


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user account."""
    if get_user_by_username(db, data.username):
        raise HTTPException(status_code=400, detail="Username already taken.")
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered.")

    user = create_user(db, data.username, data.email, data.password, data.role)
    return user


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
def login(request: Request, data: UserLogin, db: Session = Depends(get_db)):
    """Login and receive a JWT access token."""
    user = authenticate_user(db, data.username, data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
        )

    # Update last_login
    user.last_login = datetime.utcnow()
    db.commit()

    token = create_access_token({"sub": user.username, "role": user.role})
    return TokenResponse(access_token=token, user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    """Get the currently authenticated user's profile."""
    return current_user


@router.post("/logout", response_model=MessageResponse)
def logout(current_user: User = Depends(get_current_user)):
    """
    Logout endpoint.
    (JWT tokens are stateless — actual invalidation requires a token blacklist.
     For this demo, the client simply discards the token.)
    """
    return MessageResponse(message=f"User '{current_user.username}' logged out successfully.")
