import time
import httpx
import jwt
from jwt.algorithms import RSAAlgorithm
from .config import APPLE_AUDIENCE

APPLE_JWKS_URL = "https://appleid.apple.com/auth/keys"

_jwks_cache = {"ts": 0, "keys": None}

async def get_apple_jwks():
    # cache for 1 hour
    now = time.time()
    if _jwks_cache["keys"] and (now - _jwks_cache["ts"] < 3600):
        return _jwks_cache["keys"]

    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(APPLE_JWKS_URL)
        r.raise_for_status()
        data = r.json()

    _jwks_cache["ts"] = now
    _jwks_cache["keys"] = data["keys"]
    return data["keys"]

async def verify_apple_identity_token(identity_token: str) -> str:
    # Returns apple_sub (unique user id)
    header = jwt.get_unverified_header(identity_token)
    kid = header.get("kid")
    if not kid:
        raise ValueError("Apple token missing kid")

    keys = await get_apple_jwks()
    key = next((k for k in keys if k.get("kid") == kid), None)
    if not key:
        raise ValueError("Apple key not found")

    public_key = RSAAlgorithm.from_jwk(key)

    # Verify issuer + signature (+ optionally audience)
    options = {"verify_aud": bool(APPLE_AUDIENCE)}
    payload = jwt.decode(
        identity_token,
        public_key,
        algorithms=["RS256"],
        issuer="https://appleid.apple.com",
        audience=APPLE_AUDIENCE if APPLE_AUDIENCE else None,
        options=options,
    )

    sub = payload.get("sub")
    if not sub:
        raise ValueError("Apple token missing sub")
    return sub
