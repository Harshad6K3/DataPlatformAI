"""JWKS fetching and key resolution with caching.

This client fetches JWKS from an OIDC/OpenID Provider, caches
the keys for a configurable TTL (default 1 hour), and exposes a
method to obtain a PEM-formatted public key for a given `kid`.
"""
from __future__ import annotations

from typing import Dict, Optional
import time
import asyncio
import logging
import json

import httpx
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization


logger = logging.getLogger("shared.auth.jwks")


class JWKSClient:
    """Fetch JWKS and provide public keys for verification.

    Example:
        client = JWKSClient("https://login.example.com/.well-known/jwks.json")
        pub_pem = await client.get_public_key_pem(kid)
    """

    def __init__(self, jwks_url: str, ttl_seconds: int = 3600):
        self.jwks_url = jwks_url
        self.ttl_seconds = ttl_seconds
        self._keys: Dict[str, Dict] = {}
        self._last_fetch: float = 0.0
        self._lock = asyncio.Lock()

    async def _fetch(self) -> None:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(self.jwks_url)
            resp.raise_for_status()
            payload = resp.json()
            keys = {k["kid"]: k for k in payload.get("keys", [])}
            self._keys = keys
            self._last_fetch = time.time()
            logger.info(json.dumps({"event": "jwks_fetched", "count": len(keys)}))

    async def _ensure_keys(self) -> None:
        # Refresh if empty or expired
        if not self._keys or (time.time() - self._last_fetch) > self.ttl_seconds:
            async with self._lock:
                # double-check after acquiring lock
                if not self._keys or (time.time() - self._last_fetch) > self.ttl_seconds:
                    await self._fetch()

    async def get_jwk(self, kid: str) -> Optional[Dict]:
        """Return the JWK dict for `kid` or None."""
        await self._ensure_keys()
        return self._keys.get(kid)

    @staticmethod
    def _int_from_base64url(data: str) -> int:
        import base64

        rem = len(data) % 4
        if rem:
            data += "=" * (4 - rem)
        return int.from_bytes(base64.urlsafe_b64decode(data), "big")

    async def get_public_key_pem(self, kid: str) -> Optional[bytes]:
        """Return PEM-encoded public key bytes for the given `kid`.

        Returns None if the kid is not found.
        """
        jwk = await self.get_jwk(kid)
        if not jwk:
            return None
        # Expect RSA keys
        if jwk.get("kty") != "RSA":
            raise ValueError("Only RSA keys are supported")
        n = self._int_from_base64url(jwk["n"])
        e = self._int_from_base64url(jwk["e"])
        pub_numbers = rsa.RSAPublicNumbers(e, n)
        public_key = pub_numbers.public_key()
        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        return pem
