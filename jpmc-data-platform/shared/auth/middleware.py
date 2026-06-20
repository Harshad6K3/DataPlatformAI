"""FastAPI middleware implementing OAuth2/JWT authentication.

Features:
- PKCE/OAuth2 support via external IdP (Okta/Azure) by validating JWTs issued by IdP
- JWKS fetching and caching
- Mock mode for local development via header `X-Mock-User`
- Rate limiting via Redis sliding window
- Injects `request.state.user` with `AuthenticatedUser`
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
import os
import json
import logging
from datetime import datetime

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse

from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError, JWTClaimsError

from .jwks_client import JWKSClient
from .rate_limiter import RedisRateLimiter
from .mock import get_mock_user_from_request
from .models import AuthenticatedUser


logger = logging.getLogger("shared.auth.middleware")


DEFAULT_PUBLIC_PATHS = ["/health", "/ready", "/docs", "/openapi.json"]


class JWTAuthMiddleware(BaseHTTPMiddleware):
    """Middleware that validates Bearer JWTs and enforces rate limits.

    Configuration via environment variables:
    - AUTH_MODE: 'prod' or 'mock'
    - AUTH_JWKS_URL: JWKS URL of the identity provider
    - AUTH_AUDIENCE: expected audience
    - AUTH_ISSUER: expected issuer
    - AUTH_REDIS_URL: redis connection url for rate limiter
    - AUTH_MAX_REQ_PER_MIN: requests per minute (default 100)
    """

    def __init__(self, app, *, jwks_url: Optional[str] = None):
        super().__init__(app)
        self.mode = os.getenv("AUTH_MODE", "prod")
        self.jwks_url = jwks_url or os.getenv("AUTH_JWKS_URL")
        self.audience = os.getenv("AUTH_AUDIENCE")
        self.issuer = os.getenv("AUTH_ISSUER")
        redis_url = os.getenv("AUTH_REDIS_URL", "redis://localhost:6379/0")
        max_req = int(os.getenv("AUTH_MAX_REQ_PER_MIN", "100"))

        self.jwks_client = JWKSClient(self.jwks_url) if self.jwks_url else None
        self.rate_limiter = RedisRateLimiter(redis_url, max_requests=max_req, window_seconds=60)
        self.public_paths = set(DEFAULT_PUBLIC_PATHS)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        path = request.url.path
        if path in self.public_paths or request.method.upper() == "OPTIONS":
            return await call_next(request)

        ip = request.client.host if request.client else None
        ua = request.headers.get("user-agent")

        try:
            if self.mode == "mock":
                # Mock mode: accept X-Mock-User header
                mock_payload = await get_mock_user_from_request(request)
                user = AuthenticatedUser(**mock_payload)
                request.state.user = user
                return await call_next(request)

            # Production mode: expect Authorization: Bearer <token>
            auth = request.headers.get("Authorization", "")
            if not auth.startswith("Bearer "):
                return self._unauthorized_response("Missing bearer token")

            token = auth.split(" ", 1)[1]
            # Validate token header to find kid
            header = jwt.get_unverified_header(token)
            kid = header.get("kid")
            if not kid:
                return self._unauthorized_response("Token missing kid header")

            if not self.jwks_client:
                return self._unauthorized_response("JWKS client not configured")

            pub_pem = await self.jwks_client.get_public_key_pem(kid)
            if not pub_pem:
                # force a refresh and retry once
                pub_pem = await self.jwks_client.get_public_key_pem(kid)
            if not pub_pem:
                return self._unauthorized_response("Unable to find public key for token")

            try:
                decoded = jwt.decode(
                    token,
                    pub_pem,
                    algorithms=["RS256"],
                    audience=self.audience,
                    issuer=self.issuer,
                )
            except ExpiredSignatureError:
                self._log_failure(ip, ua, "token_expired")
                return self._unauthorized_response("Token expired")
            except JWTClaimsError as exc:
                self._log_failure(ip, ua, f"invalid_claims: {str(exc)}")
                return self._unauthorized_response("Invalid token claims")
            except JWTError as exc:
                self._log_failure(ip, ua, f"jwt_error: {str(exc)}")
                return self._unauthorized_response("Invalid token")

            # Extract identity
            user_id = decoded.get("sub") or decoded.get("client_id") or decoded.get("uid")
            email = decoded.get("email")
            roles = decoded.get("roles") or decoded.get("role") or []
            if isinstance(roles, str):
                roles = [roles]
            domains = decoded.get("domains") or decoded.get("hd") or []
            if isinstance(domains, str):
                domains = [domains]

            is_service = bool(decoded.get("client_id") or decoded.get("azp")) and not email

            if not user_id:
                self._log_failure(ip, ua, "missing_sub")
                return self._unauthorized_response("Token missing subject")

            # Rate limit per user_id
            allowed = await self.rate_limiter.allow(user_id)
            if not allowed:
                self._log_failure(ip, ua, "rate_limited")
                return JSONResponse(status_code=429, content={"detail": "Too Many Requests"})

            user = AuthenticatedUser(
                user_id=str(user_id),
                email=email,
                roles=list(roles),
                domains=list(domains),
                is_service_account=is_service,
            )
            request.state.user = user

        except Exception as exc:
            # Ensure we never leak tokens in logs
            self._log_failure(ip, ua, f"unexpected_error: {str(exc)}")
            return self._unauthorized_response("Authentication failed")

        return await call_next(request)

    def _unauthorized_response(self, reason: str):
        headers = {"WWW-Authenticate": 'Bearer realm="api", error="invalid_token"'}
        return JSONResponse(status_code=401, content={"detail": reason}, headers=headers)

    def _log_failure(self, ip: Optional[str], ua: Optional[str], reason: str) -> None:
        logger.info(json.dumps({"timestamp": datetime.utcnow().isoformat(), "ip": ip, "user_agent": ua, "failure_reason": reason}))
