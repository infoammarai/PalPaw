import jwt
from datetime import datetime, timedelta, timezone
from .config import JWT_SECRET

def sign_access_token(user_id: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "uid": user_id,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(days=30)).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def verify_access_token(token: str) -> str:
    payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    uid = payload.get("uid")
    if not uid:
        raise ValueError("Invalid token: missing uid")
    return uid
