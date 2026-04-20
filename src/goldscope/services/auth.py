from datetime import timedelta

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from goldscope.core.config import get_settings
from goldscope.core.security import create_access_token, hash_password, verify_password
from goldscope.models.user import User
from goldscope.schemas.auth import LoginRequest, RegisterRequest, TokenResponse


def register_user(db: Session, payload: RegisterRequest) -> User:
    existing_user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with that email already exists.",
        )

    user = User(
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login_user(db: Session, payload: LoginRequest) -> TokenResponse:
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    settings = get_settings()
    access_token, expires_at = create_access_token(
        subject=str(user.id),
        settings=settings,
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    return TokenResponse(access_token=access_token, expires_at=expires_at, user=user)
