# tests/auth/test_auth.py
import os
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from shared.auth import AuthenticatedUser, JWTAuthMiddleware, get_current_user


def create_app(auth_mode: str = "mock") -> TestClient:
    os.environ["AUTH_MODE"] = auth_mode
    app = FastAPI()
    app.add_middleware(JWTAuthMiddleware)

    @app.get("/protected")
    async def protected(user: AuthenticatedUser = Depends(get_current_user)):
        return {"user_id": user.user_id, "email": user.email}

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    return TestClient(app)

def test_health_no_auth_needed():
    client = create_app(auth_mode="mock")
    response = client.get("/health")
    assert response.status_code == 200

def test_protected_with_mock_user():
    client = create_app(auth_mode="mock")
    response = client.get(
        "/protected",
        headers={"X-Mock-User": '{"user_id":"u1","email":"test@bank.com","roles":["engineer"],"domains":["all"],"is_service_account":false}'}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "test@bank.com"

def test_protected_no_auth_fails():
    client = create_app(auth_mode="jwt")
    response = client.get("/protected")
    assert response.status_code == 401