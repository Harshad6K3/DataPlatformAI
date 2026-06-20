"""Authentication helpers for shared services.

This package exposes a production-grade FastAPI authentication
middleware, JWKS client, Redis-backed rate limiter, and helpers
for mock/local development.
"""

__all__ = [
	"AuthenticatedUser",
	"JWTAuthMiddleware",
	"get_current_user",
	"JWKSClient",
	"RedisRateLimiter",
	"parse_mock_user",
]
