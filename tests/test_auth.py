from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.security import create_access_token
from app.main import app

client = TestClient(app)


def test_register_user():
    email = f"test-{uuid4()}@example.com"

    response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "TestPassword123",
            "full_name": "Test User",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["email"] == email
    assert data["full_name"] == "Test User"
    assert data["role"] == "customer"
    assert "password" not in data
    assert "password_hash" not in data


def test_duplicate_email():
    email = f"duplicate-{uuid4()}@example.com"

    payload = {
        "email": email,
        "password": "TestPassword123",
        "full_name": "Duplicate Test",
    }

    first_response = client.post(
        "/auth/register",
        json=payload,
    )

    second_response = client.post(
        "/auth/register",
        json=payload,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409

    assert second_response.json()["detail"] == "Email already registered"


def test_login_success():
    email = f"login-{uuid4()}@example.com"

    register_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "TestPassword123",
            "full_name": "Login Test",
        },
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "TestPassword123",
        },
    )

    assert login_response.status_code == 200

    data = login_response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 0


def test_login_wrong_password():
    email = f"wrong-password-{uuid4()}@example.com"

    register_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "TestPassword123",
            "full_name": "Wrong Password Test",
        },
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "WrongPassword123",
        },
    )

    assert login_response.status_code == 401
    assert login_response.json()["detail"] == "Invalid email or password"


def test_login_unknown_email():
    response = client.post(
        "/auth/login",
        json={
            "email": f"unknown-{uuid4()}@example.com",
            "password": "TestPassword123",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_auth_me_without_token():
    response = client.get("/auth/me")

    assert response.status_code == 401


def test_auth_me_with_invalid_token():
    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid.token.value"},
    )

    assert response.status_code == 401


def test_auth_me_with_valid_token():
    email = f"me-{uuid4()}@example.com"

    register_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "TestPassword123",
            "full_name": "Me Test",
        },
    )

    assert register_response.status_code == 201

    user = register_response.json()

    token = create_access_token(str(user["id"]))

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == user["id"]
    assert data["email"] == email
    assert data["full_name"] == "Me Test"
    assert data["role"] == "customer"


def test_register_rejects_whitespace_only_full_name():
    response = client.post(
        "/auth/register",
        json={
            "email": f"validation-{uuid4()}@example.com",
            "password": "TestPassword123",
            "full_name": "   ",
        },
    )

    assert response.status_code == 422


def test_login_rejects_empty_password():
    response = client.post(
        "/auth/login",
        json={
            "email": f"validation-{uuid4()}@example.com",
            "password": "",
        },
    )

    assert response.status_code == 422
