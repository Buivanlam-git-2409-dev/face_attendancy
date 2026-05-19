import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import jwt


SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_HOURS = int(os.getenv("ACCESS_TOKEN_EXPIRE_HOURS", "24"))


def hash_password(password: str) -> str:
    if not password:
        raise ValueError("Password cannot be empty")

    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    if not password or not hashed:
        return False

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


def generate_refresh_token(user_id: int, role: str, is_admin: bool = False) -> str:
    now = datetime.now(timezone.utc)

    payload = {
        "user_id": user_id,
        "role": role,
        "is_admin": is_admin,
        "type": "refresh",
        "iat": now,
        "exp": now + timedelta(days=7),
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)


def verify_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])

        if payload.get("type") == "refresh":
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


def token_required(*args, **kwargs):
    raise NotImplementedError(
        "token_required is legacy Flask auth and should not be used in FastAPI JWT flow."
    )