from fastapi import APIRouter, status

from goldscope.api.deps import DbSession
from goldscope.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserRead
from goldscope.services.auth import login_user, register_user

router = APIRouter()


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: DbSession) -> UserRead:
    return register_user(db, payload)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: DbSession) -> TokenResponse:
    return login_user(db, payload)
