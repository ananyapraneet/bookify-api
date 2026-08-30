import json

from uuid import uuid4
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.core.redis import get_redis
from app.core.security import create_access_token
from app.db.database import SessionLocal
from app.main import app
from app.models.service import Service
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


def create_test_service(owner_id: int) -> Service:
    db = SessionLocal()

    try:
        service = Service(
            name=f"Test Service {uuid4()}",
            description="Test service",
            price=500.00,
            duration_minutes=30,
            owner_id=owner_id,
        )

        db.add(service)
        db.commit()
        db.refresh(service)

        return service
    finally:
        db.close()


def test_create_service_as_provider():
    user = create_test_user(UserRole.PROVIDER)

    response = client.post(
        "/services",
        headers=get_auth_headers(user),
        json={
            "name": "Test Haircut",
            "description": "Test haircut service",
            "price": 799.00,
            "duration_minutes": 45,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Test Haircut"
    assert data["description"] == "Test haircut service"
    assert data["price"] == "799.00"
    assert data["duration_minutes"] == 45
    assert data["owner_id"] == user.id


def test_customer_cannot_create_service():
    user = create_test_user(UserRole.CUSTOMER)

    response = client.post(
        "/services",
        headers=get_auth_headers(user),
        json={
            "name": "Customer Service",
            "description": "Should not be created",
            "price": 500.00,
            "duration_minutes": 30,
        },
    )

    assert response.status_code == 403

    assert response.json()["detail"] == (
        "Only providers and admins can create services"
    )


def test_customer_can_list_services():
    user = create_test_user(UserRole.CUSTOMER)

    service = create_test_service(user.id)

    response = client.get(
        "/services",
        headers=get_auth_headers(user),
    )

    assert response.status_code == 200

    data = response.json()

    assert any(
        item["id"] == service.id
        for item in data
    )

def test_list_services_uses_redis_cache_hit():

    user = create_test_user(UserRole.CUSTOMER)

    cached_service = {
        "id": 999999,
        "name": "Cached Service",
        "description": "Returned from Redis",
        "price": "799.00",
        "duration_minutes": 45,
        "owner_id": user.id,
        "created_at": "2026-08-31T10:00:00Z",
        "updated_at": "2026-08-31T10:00:00Z",
    }

    mock_redis = AsyncMock()

    mock_redis.get.return_value = json.dumps(
        [cached_service]
    )

    app.dependency_overrides[
        get_redis
    ] = lambda: mock_redis

    try:
        response = client.get(
            "/services",
            headers=get_auth_headers(user),
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == [cached_service]

    mock_redis.get.assert_awaited_once_with(
        "services:list"
    )

    mock_redis.set.assert_not_awaited()

def test_get_service():
    user = create_test_user(UserRole.PROVIDER)
    service = create_test_service(user.id)

    response = client.get(
        f"/services/{service.id}",
        headers=get_auth_headers(user),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == service.id
    assert data["name"] == service.name
    assert data["owner_id"] == user.id


def test_get_nonexistent_service():
    user = create_test_user(UserRole.PROVIDER)

    response = client.get(
        "/services/999999",
        headers=get_auth_headers(user),
    )

    assert response.status_code == 404

    assert response.json()["detail"] == "Service not found"


def test_provider_can_update_own_service():
    user = create_test_user(UserRole.PROVIDER)
    service = create_test_service(user.id)

    response = client.patch(
        f"/services/{service.id}",
        headers=get_auth_headers(user),
        json={
            "name": "Updated Service",
            "price": 899.00,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Updated Service"
    assert data["price"] == "899.00"
    assert data["duration_minutes"] == 30
    assert data["owner_id"] == user.id


def test_customer_cannot_update_service():
    provider = create_test_user(UserRole.PROVIDER)
    customer = create_test_user(UserRole.CUSTOMER)

    service = create_test_service(provider.id)

    response = client.patch(
        f"/services/{service.id}",
        headers=get_auth_headers(customer),
        json={
            "price": 999.00,
        },
    )

    assert response.status_code == 403

    assert response.json()["detail"] == (
        "You do not have permission to update this service"
    )


def test_provider_cannot_update_another_providers_service():
    provider_one = create_test_user(UserRole.PROVIDER)
    provider_two = create_test_user(UserRole.PROVIDER)

    service = create_test_service(provider_one.id)

    response = client.patch(
        f"/services/{service.id}",
        headers=get_auth_headers(provider_two),
        json={
            "price": 999.00,
        },
    )

    assert response.status_code == 403

    assert response.json()["detail"] == (
        "You do not have permission to update this service"
    )


def test_admin_can_update_another_providers_service():
    provider = create_test_user(UserRole.PROVIDER)
    admin = create_test_user(UserRole.ADMIN)

    service = create_test_service(provider.id)

    response = client.patch(
        f"/services/{service.id}",
        headers=get_auth_headers(admin),
        json={
            "price": 999.00,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["price"] == "999.00"
    assert data["owner_id"] == provider.id


def test_customer_cannot_delete_service():
    provider = create_test_user(UserRole.PROVIDER)
    customer = create_test_user(UserRole.CUSTOMER)

    service = create_test_service(provider.id)

    response = client.delete(
        f"/services/{service.id}",
        headers=get_auth_headers(customer),
    )

    assert response.status_code == 403

    assert response.json()["detail"] == (
        "You do not have permission to delete this service"
    )


def test_provider_cannot_delete_another_providers_service():
    provider_one = create_test_user(UserRole.PROVIDER)
    provider_two = create_test_user(UserRole.PROVIDER)

    service = create_test_service(provider_one.id)

    response = client.delete(
        f"/services/{service.id}",
        headers=get_auth_headers(provider_two),
    )

    assert response.status_code == 403

    assert response.json()["detail"] == (
        "You do not have permission to delete this service"
    )


def test_provider_can_delete_own_service():
    provider = create_test_user(UserRole.PROVIDER)

    service = create_test_service(provider.id)

    response = client.delete(
        f"/services/{service.id}",
        headers=get_auth_headers(provider),
    )

    assert response.status_code == 204
    assert response.content == b""

    db = SessionLocal()

    try:
        deleted_service = db.get(Service, service.id)
        assert deleted_service is None
    finally:
        db.close()


def test_admin_can_delete_another_providers_service():
    provider = create_test_user(UserRole.PROVIDER)
    admin = create_test_user(UserRole.ADMIN)

    service = create_test_service(provider.id)

    response = client.delete(
        f"/services/{service.id}",
        headers=get_auth_headers(admin),
    )

    assert response.status_code == 204

    db = SessionLocal()

    try:
        deleted_service = db.get(Service, service.id)
        assert deleted_service is None
    finally:
        db.close()


def test_create_service_invalid_price():
    provider = create_test_user(UserRole.PROVIDER)

    response = client.post(
        "/services",
        headers=get_auth_headers(provider),
        json={
            "name": "Invalid Price Service",
            "description": "Invalid price",
            "price": 0,
            "duration_minutes": 30,
        },
    )

    assert response.status_code == 422


def test_create_service_invalid_duration():
    provider = create_test_user(UserRole.PROVIDER)

    response = client.post(
        "/services",
        headers=get_auth_headers(provider),
        json={
            "name": "Invalid Duration Service",
            "description": "Invalid duration",
            "price": 500.00,
            "duration_minutes": 0,
        },
    )

    assert response.status_code == 422


def test_create_service_missing_required_fields():
    provider = create_test_user(UserRole.PROVIDER)

    response = client.post(
        "/services",
        headers=get_auth_headers(provider),
        json={
            "description": "Missing required fields",
        },
    )

    assert response.status_code == 422


def test_services_require_authentication():
    response = client.get("/services")

    assert response.status_code == 401

def test_create_service_rejects_whitespace_only_name():
    user = create_test_user(UserRole.PROVIDER)
    response = client.post(
        "/services",
        headers=get_auth_headers(user),
        json={
            "name": "   ",
            "description": "Invalid service name",
            "price": 500.00,
            "duration_minutes": 30,
        },
    )

    assert response.status_code == 422

def test_create_service_strips_name_whitespace():
    user = create_test_user(UserRole.PROVIDER)
    response = client.post(
        "/services",
        headers=get_auth_headers(user),
        json={
            "name": "  Test Haircut  ",
            "description": "Test service",
            "price": 500.00,
            "duration_minutes": 30,
        },
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Test Haircut"

def test_create_service_invalidates_cache():
    user = create_test_user(UserRole.PROVIDER)

    response = client.post(
        "/services",
        headers=get_auth_headers(user),
        json={
            "name": "Cached Service",
            "description": "Cache invalidation test",
            "price": 500.00,
            "duration_minutes": 30,
        },
    )

    assert response.status_code == 201

def test_list_services_uses_database_on_redis_cache_miss():
    user = create_test_user(UserRole.CUSTOMER)
    service = create_test_service(user.id)

    mock_redis = AsyncMock()
    mock_redis.get.return_value = None

    app.dependency_overrides[
        get_redis
    ] = lambda: mock_redis

    try:
        response = client.get(
            "/services",
            headers=get_auth_headers(user),
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200

    data = response.json()

    assert any(
        item["id"] == service.id
        for item in data
    )

    mock_redis.get.assert_awaited_once_with(
        "services:list"
    )

    mock_redis.set.assert_awaited_once()

    set_args = mock_redis.set.await_args

    assert set_args.args[0] == "services:list"
    assert set_args.kwargs["ex"] == 60

def test_update_service_invalidates_cache():
    provider = create_test_user(UserRole.PROVIDER)

    create_response = client.post(
        "/services",
        json={
            "name": "Original Service",
            "description": "Original Description",
            "price": "500.00",
            "duration_minutes": 30,
        },
        headers=get_auth_headers(provider),
    )

    assert create_response.status_code == 201

    service = create_response.json()

    mock_redis = AsyncMock()

    app.dependency_overrides[get_redis] = lambda: mock_redis

    try:
        response = client.patch(
            f"/services/{service['id']}",
            json={
                "name": "Updated Service",
            },
            headers=get_auth_headers(provider),
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200

    mock_redis.delete.assert_awaited_once_with(
        "services:list"
    )

def test_delete_service_invalidates_cache():
    provider = create_test_user(UserRole.PROVIDER)

    create_response = client.post(
        "/services",
        json={
            "name": "Service To Delete",
            "description": "Service for deletion test",
            "price": "500.00",
            "duration_minutes": 30,
        },
        headers=get_auth_headers(provider),
    )

    assert create_response.status_code == 201

    service = create_response.json()

    mock_redis = AsyncMock()

    app.dependency_overrides[get_redis] = lambda: mock_redis

    try:
        response = client.delete(
            f"/services/{service['id']}",
            headers=get_auth_headers(provider),
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 204

    mock_redis.delete.assert_awaited_once_with(
        "services:list"
    )
