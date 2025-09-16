import bcrypt
import datetime as dt
import jwt
from django.conf import settings

def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()

def check_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    except Exception:
        return False

def _now_utc():
    return dt.datetime.now(dt.timezone.utc)

def make_token(user_id: int, ttl_minutes: int, token_type: str = "access") -> str:
    payload = {
        "sub": str(user_id),
        "type": token_type,
        "iat": int(_now_utc().timestamp()),
        "exp": int((_now_utc() + dt.timedelta(minutes=ttl_minutes)).timestamp()),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)

def make_access(user_id: int) -> str:
    ttl = int(getattr(settings, "JWT_ACCESS_TTL_MIN", 15))
    return make_token(user_id, ttl, "access")

def make_refresh(user_id: int) -> str:
    days = int(getattr(settings, "JWT_REFRESH_TTL_DAYS", 7))
    return make_token(user_id, days * 24 * 60, "refresh")

def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
