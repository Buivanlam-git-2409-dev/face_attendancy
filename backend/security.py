import os
from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import Optional

import bcrypt
import jwt


SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_HOURS = int(os.getenv("ACCESS_TOKEN_EXPIRE_HOURS", "24"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))


def hash_password(password: str) -> str:
    if not password:
        raise ValueError("Password cannot be empty")

    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    if not password or not hashed:
        return False

    # Old plain-text passwords are intentionally rejected here.
    # Migration to hashed passwords should happen in AuthService.
    if not hashed.startswith("$2"):
        return False

    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            hashed.encode("utf-8"),
        )
    except ValueError:
        return False


def generate_token(
    user_id: int,
    role: str,
    is_admin: bool = False,
    expires_in_hours: Optional[int] = None,
) -> str:
    now = datetime.now(timezone.utc)
    expire_hours = expires_in_hours or ACCESS_TOKEN_EXPIRE_HOURS

    payload = {
        "user_id": user_id,
        "role": role,
        "is_admin": is_admin,
        "type": "access",
        "iat": now,
        "exp": now + timedelta(hours=expire_hours),
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)


def generate_refresh_token(
    user_id: int,
    role: str,
    is_admin: bool = False,
    expires_in_days: Optional[int] = None,
) -> str:
    now = datetime.now(timezone.utc)
    expire_days = expires_in_days or REFRESH_TOKEN_EXPIRE_DAYS

    payload = {
        "user_id": user_id,
        "role": role,
        "is_admin": is_admin,
        "type": "refresh",
        "iat": now,
        "exp": now + timedelta(days=expire_days),
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)


def verify_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])

        if payload.get("type") != "access":
            return None
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def verify_refresh_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])

        if payload.get("type") != "refresh":
            return None

        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def token_required(func):
    """
    Legacy Flask compatibility only.

    Do not use this for new FastAPI routes.
    FastAPI routes must use dependencies from:
    backend/api/v1/dependencies.py
    """
    @wraps(func)
    def decorated(*args, **kwargs):
        return func(*args, **kwargs)
    return decorated

def require_jwt(func):
    return token_required(func)

def require_student(func):
    return token_required(func)

def require_faculty(func):
    return token_required(func)

def require_admin(func):
    return token_required(func)