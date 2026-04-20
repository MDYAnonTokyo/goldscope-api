from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt
from passlib.context import CryptContext

from goldscope.core.config import Settings

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    *,
    subject: str,
    settings: Settings,
    expires_delta: timedelta | None = None,
) -> tuple[str, datetime]:
    now = datetime.now(UTC)
    expire_at = now + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    to_encode = {
        "sub": subject,
        "iss": settings.token_issuer,
        "aud": settings.token_audience,
        "iat": int(now.timestamp()),
        "exp": int(expire_at.timestamp()),
    }
    token = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return token, expire_at


def decode_access_token(*, token: str, settings: Settings) -> dict:
    return jwt.decode(
        token,
        settings.secret_key,
        algorithms=[settings.algorithm],
        audience=settings.token_audience,
        issuer=settings.token_issuer,
    )


def is_jwt_error(exc: Exception) -> bool:
    return isinstance(exc, JWTError)
