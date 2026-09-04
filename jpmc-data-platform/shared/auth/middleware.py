"""FastAPI middleware implementing JWT authentication."""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from typing import Optional

from fastapi import Request
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTClaimsError, JWTError
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse

from .jwks_client import JWKSClient
from .mock import get_mock_user_from_request
from .models import AuthenticatedUser


logger = logging.getLogger("shared.auth.middleware")

PUBLIC_PATHS = {"/health", "/ready", "/docs", "/openapi.json"}


class JWTAuthMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware that validates JWTs and injects authenticated users."""

    def __init__(self, app, *, jwks_url: Optional[str] = None):
        super().__init__(app)
        self.mode = os.getenv("AUTH_MODE", "jwt").lower()
        self.jwks_url = jwks_url or os.getenv("AUTH_JWKS_URL")
        self.audience = os.getenv("AUTH_AUDIENCE")
        self.issuer = os.getenv("AUTH_ISSUER")
        self.jwks_client = JWKSClient(self.jwks_url) if self.jwks_url else None

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        # Default: no user
        request.state.user = None

        path = request.url.path
        if path in PUBLIC_PATHS or request.method.upper() == "OPTIONS":
            return await call_next(request)

        ip = request.client.host if request.client else None
        ua = request.headers.get("user-agent")

        if self.mode == "mock":
            try:
                user = await get_mock_user_from_request(request)
                request.state.user = user
                return await call_next(request)
            except ValueError as exc:
                logger.info(self._log_payload(ip, ua, "mock_header_missing"))
                return self._unauthorized_response(str(exc))

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            logger.info(self._log_payload(ip, ua, "missing_bearer_token"))
            return self._unauthorized_response("Missing bearer token")

        token = auth_header.split(" ", 1)[1].strip()
        try:
            header = jwt.get_unverified_header(token)
        except JWTError as exc:
            logger.info(self._log_payload(ip, ua, f"invalid_token_header:{exc}"))
            return self._unauthorized_response("Invalid token header")

        kid = header.get("kid")
        if not kid:
            logger.info(self._log_payload(ip, ua, "missing_kid"))
            return self._unauthorized_response("Token missing kid header")

        if not self.jwks_client:
            logger.error(self._log_payload(ip, ua, "jwks_not_configured"))
            return self._unauthorized_response("Authentication provider not configured")

        pub_pem = await self.jwks_client.get_public_key_pem(kid)
        if not pub_pem:
            logger.info(self._log_payload(ip, ua, "kid_not_found"))
            return self._unauthorized_response("Unable to resolve signing key")

        try:
            decoded = jwt.decode(
                token,
                pub_pem,
                algorithms=["RS256"],
                audience=self.audience,
                issuer=self.issuer,
            )
        except ExpiredSignatureError:
            logger.info(self._log_payload(ip, ua, "token_expired"))
            return self._unauthorized_response("Token expired")
        except JWTClaimsError as exc:
            logger.info(self._log_payload(ip, ua, f"invalid_claims:{exc}"))
            return self._unauthorized_response("Invalid token claims")
        except JWTError as exc:
            logger.info(self._log_payload(ip, ua, f"jwt_decode_error:{exc}"))
            return self._unauthorized_response("Invalid token")

        user_id = decoded.get("sub") or decoded.get("client_id") or decoded.get("uid")
        email = decoded.get("email") or ""
        roles = decoded.get("roles") or decoded.get("role") or []
        if isinstance(roles, str):
            roles = [roles]
        domains = decoded.get("domains") or decoded.get("hd") or []
        if isinstance(domains, str):
            domains = [domains]

        if not user_id:
            logger.info(self._log_payload(ip, ua, "missing_subject"))
            return self._unauthorized_response("Token missing subject")

        request.state.user = AuthenticatedUser(
            user_id=str(user_id),
            email=str(email),
            roles=list(roles),
            domains=list(domains),
            is_service_account=bool(
                decoded.get("client_id") or decoded.get("azp")
            ) and not bool(email),
        )

        return await call_next(request)

    def _unauthorized_response(self, reason: str) -> JSONResponse:
        return JSONResponse(status_code=401, content={"detail": reason})

    def _log_payload(self, ip: Optional[str], ua: Optional[str], reason: str) -> str:
        return json.dumps({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "ip": ip,
            "user_agent": ua,
            "reason": reason,
        })