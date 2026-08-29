from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.security import create_access_token
from app.db.database import SessionLocal
from app.main import app
from app.models.user import User, UserRole


client = TestClient(app)


def create_test_user(role: UserRole) -> User:
    db = SessionLocal()

    try:
        user = User(
            email=f"{role.value}-{uuid4()}@example.com",
            password_hash="test-password-hash",
            full_name=f"{role.value.title()} Test User",
            role=role,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    finally:
        db.close()


def get_auth_headers(user: User) -> dict[str, str]:
    token = create_access_token(str(user.id))

    return {
        "Authorization": f"Bearer {token}"
    }


def test_roles_without_token():
    endpoints = [
        "/roles/customer",
        "/roles/provider",
        "/roles/admin",
    ]

    for endpoint in endpoints:
        response = client.get(endpoint)

        assert response.status_code == 401


def test_customer_access():
    user = create_test_user(UserRole.CUSTOMER)

    response = client.get(
        "/roles/customer",
        headers=get_auth_headers(user),
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Customer access granted"
    assert response.json()["user_id"] == user.id
    assert response.json()["role"] == "customer"


def test_customer_cannot_access_provider():
    user = create_test_user(UserRole.CUSTOMER)

    response = client.get(
        "/roles/provider",
        headers=get_auth_headers(user),
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Insufficient permissions"


def test_customer_cannot_access_admin():
    user = create_test_user(UserRole.CUSTOMER)

    response = client.get(
        "/roles/admin",
        headers=get_auth_headers(user),
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Insufficient permissions"


def test_provider_access():
    user = create_test_user(UserRole.PROVIDER)

    response = client.get(
        "/roles/provider",
        headers=get_auth_headers(user),
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Provider access granted"
    assert response.json()["user_id"] == user.id
    assert response.json()["role"] == "provider"


def test_provider_cannot_access_customer():
    user = create_test_user(UserRole.PROVIDER)

    response = client.get(
        "/roles/customer",
        headers=get_auth_headers(user),
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Insufficient permissions"


def test_provider_cannot_access_admin():
    user = create_test_user(UserRole.PROVIDER)

    response = client.get(
        "/roles/admin",
        headers=get_auth_headers(user),
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Insufficient permissions"


def test_admin_access():
    user = create_test_user(UserRole.ADMIN)

    response = client.get(
        "/roles/admin",
        headers=get_auth_headers(user),
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Admin access granted"
    assert response.json()["user_id"] == user.id
    assert response.json()["role"] == "admin"


def test_admin_cannot_access_customer():
    user = create_test_user(UserRole.ADMIN)

    response = client.get(
        "/roles/customer",
        headers=get_auth_headers(user),
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Insufficient permissions"


def test_admin_cannot_access_provider():
    user = create_test_user(UserRole.ADMIN)

    response = client.get(
        "/roles/provider",
        headers=get_auth_headers(user),
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Insufficient permissions"
