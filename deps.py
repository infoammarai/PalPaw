from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session
from .db import SessionLocal
from .auth_jwt import verify_access_token

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def require_user_id(authorization: str = Header(default="")) -> str:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="missing_token")
    token = authorization[7:]
    try:
        return verify_access_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="invalid_token")
