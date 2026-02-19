import os

def must(name: str) -> str:
    v = os.getenv(name)
    if not v:
        raise RuntimeError(f"Missing env var: {name}")
    return v

DATABASE_URL = must("DATABASE_URL")  # Render provides this for Postgres
JWT_SECRET = must("JWT_SECRET")      # set in Render env
APPLE_AUDIENCE = os.getenv("APPLE_AUDIENCE")  # set later (bundle id / services id)
