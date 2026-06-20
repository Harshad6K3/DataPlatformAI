"""JWT utilities and FastAPI middleware for authentication.

This module provides:
- `JWTSettings` pydantic settings for configuration
- `create_access_token` / `decode_token` helpers
- `JWTMiddleware` Starlette middleware that validates bearer tokens
- `get_current_user` dependency to access the token payload

All secrets are read from environment variables via `JWTSettings`.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
import os
import time
import json
import logging
from datetime import datetime, timedelta

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse

try:
    import jwt  # PyJWT
except Exception as exc:  # pragma: no cover - runtime dependency
    raise RuntimeError("PyJWT is required: add 'PyJWT' to your dependencies") from exc

from pydantic_settings import BaseSettings


class JWTSettings(BaseSettings):
    """Pydantic settings for JWT configuration.

    Environment variables (prefix `JWT_`) are used to populate fields.
    Examples:
    - `JWT_SECRET_KEY` for HS algorithms
    - `JWT_PUBLIC_KEY`/`JWT_PRIVATE_KEY` for RS algorithms
    - `JWT_ALGORITHM` e.g. `HS256` or `RS256`
    """

    algorithm: str = "HS256"
    secret_key: Optional[str] = None
    public_key: Optional[str] = None
    private_key: Optional[str] = None
    access_token_expire_minutes: int = 60
    issuer: Optional[str] = None
    audience: Optional[str] = None
    exclude_paths: List[str] = []

    class Config:
        env_prefix = "JWT_"


def _logger() -> logging.Logger:
    """Return a structured JSON-capable logger for this module."""
    logger = logging.getLogger("shared.auth.jwt")
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


def _signing_key(settings: JWTSettings) -> str:
    """Return the correct signing key based on algorithm and settings.

    Raises ValueError if the required secret/key is missing.
    """
    alg = (settings.algorithm or "").upper()
    if alg.startswith("RS"):
        if not settings.private_key and not settings.public_key:
            raise ValueError("RSA algorithm configured but no private/public key provided")
        # For encoding we need private key; for decoding public key may suffice
        return settings.private_key or settings.public_key  # type: ignore[return-value]

    # default to HMAC
    if not settings.secret_key:
        raise ValueError("HS algorithm configured but JWT_SECRET_KEY is not set")
    return settings.secret_key


def create_access_token(subject: Dict[str, Any], settings: JWTSettings) -> str:
    """Create a signed JWT access token for `subject` payload.

    The payload will be copied and augmented with standard claims:
    - `iat`, `exp`, optional `iss`, `aud`.
    """
    now = datetime.utcnow()
    to_encode = subject.copy()
    to_encode.update({"iat": int(now.timestamp())})
    expire = now + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": int(expire.timestamp())})
    if settings.issuer:
        to_encode["iss"] = settings.issuer
    if settings.audience:
        to_encode["aud"] = settings.audience

    key = _signing_key(settings)
    token = jwt.encode(to_encode, key, algorithm=settings.algorithm)
    return token


def decode_token(token: str, settings: JWTSettings) -> Dict[str, Any]:
    """Decode and validate a JWT token. Raises HTTPException on failure.

    Returns the token payload as a dict.
    """
    logger = _logger()
    try:
        key = _signing_key(settings)
        options: Dict[str, Any] = {"require_exp": True}
        decoded = jwt.decode(
            token,
            key,
            algorithms=[settings.algorithm],
            audience=settings.audience if settings.audience else None,
            issuer=settings.issuer if settings.issuer else None,
            options=options,
        )
        logger.info(json.dumps({"event": "jwt_decoded", "sub": decoded.get("sub")}))
        return decoded
    except jwt.ExpiredSignatureError:
        logger.info(json.dumps({"event": "jwt_expired"}))
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidAudienceError:
        logger.info(json.dumps({"event": "jwt_invalid_audience"}))
        raise HTTPException(status_code=401, detail="Invalid token audience")
    except jwt.InvalidIssuerError:
        logger.info(json.dumps({"event": "jwt_invalid_issuer"}))
        raise HTTPException(status_code=401, detail="Invalid token issuer")
    except jwt.PyJWTError as exc:
        logger.info(json.dumps({"event": "jwt_error", "error": str(exc)}))
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")


class JWTMiddleware(BaseHTTPMiddleware):
    """Starlette middleware that validates incoming Bearer JWTs.

    On success the decoded payload is attached to `request.state.user`.
    Paths listed in `settings.exclude_paths` are bypassed.
    """

    def __init__(self, app, settings: Optional[JWTSettings] = None):
        super().__init__(app)
        self.settings = settings or JWTSettings()
        self.logger = _logger()

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        path = request.url.path
        if path in self.settings.exclude_paths or request.method.upper() == "OPTIONS":
            return await call_next(request)

        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            self.logger.info(json.dumps({"event": "missing_auth", "path": path}))
            return JSONResponse(status_code=401, content={"detail": "Missing Authorization header"})

        token = auth.split(" ", 1)[1]
        try:
            payload = decode_token(token, self.settings)
            # attach to request state for downstream handlers/dependencies
            request.state.user = payload
        except HTTPException as ex:
            return JSONResponse(status_code=ex.status_code, content={"detail": ex.detail})

        return await call_next(request)


async def get_current_user(request: Request) -> Dict[str, Any]:
    """FastAPI dependency that returns the decoded token payload from `request.state`.

    Raises `HTTPException` 401 if no authenticated user is present.
    """
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthenticated")
    return user
