import datetime
import re
import secrets
import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def now_my() -> datetime.datetime:
    """Return timezone-aware current datetime in Asia/Kuala_Lumpur (GMT+8)."""
    return datetime.datetime.now(settings.TIMEZONE)


def now_my_naive() -> datetime.datetime:
    """Return naive current datetime normalized to Asia/Kuala_Lumpur (GMT+8)."""
    return now_my().replace(tzinfo=None)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def validate_password_strength(password: str) -> str | None:
    """Validate password complexity rules. Returns error message or None if valid."""
    if len(password) < 8:
        return "Password must be at least 8 characters long."
    if len(password) > 70:
        return "Password cannot exceed 70 characters."
    if not re.search(r"[A-Z]", password):
        return "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return "Password must contain at least one lowercase letter."
    if not re.search(r"\d", password):
        return "Password must contain at least one number."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>\-_=+\[\]\\/;'`~]", password):
        return "Password must contain at least one special character."
    return None


def generate_otp() -> str:
    """Generate a cryptographically secure 6-digit numeric OTP."""
    return str(secrets.randbelow(900000) + 100000)


def create_access_token(username: str) -> str:
    """Create a signed HS256 JWT access token with Malaysia time expiration."""
    expiration = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        hours=settings.ACCESS_TOKEN_EXPIRE_HOURS
    )
    return jwt.encode(
        {"sub": username, "exp": expiration},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
