"""Basic tests for JWTAuthMiddleware behaviors (mocked dependencies)."""
import os
import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from shared.auth.middleware import JWTAuthMiddleware
from shared.auth.models import AuthenticatedUser


def create_app(auth_mode: str = "mock") -> FastAPI:
    os.environ["AUTH_MODE"] = auth_mode
    app = FastAPI()
    app.add_middleware(JWTAuthMiddleware)

    @app.get("/health")
    def health():
        return {"ok": True}

    @app.get("/private")
    def private(request: Request):  # explicit Request type hint — this was the bug
        user = request.state.user if hasattr(request.state, "user") else None
        return {"user": user.model_dump() if isinstance(user, AuthenticatedUser) else user}

    return app


def test_mock_mode_accepts_x_mock_user():
    app = create_app()
    client = TestClient(app)
    headers = {"X-Mock-User": '{"user_id": "u1", "email": "a@b.com", "roles": ["dev"], "domains": [], "is_service_account": false}'}
    resp = client.get("/private", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["user"]["user_id"] == "u1"