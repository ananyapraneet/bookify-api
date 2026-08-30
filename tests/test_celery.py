from unittest.mock import patch

from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.celery import celery_app
from app.core.security import create_access_token
from app.db.database import SessionLocal
from app.main import app
from app.models.service import Service
from app.models.user import User, UserRole
from app.tasks.notifications import send_booking_confirmation


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


def create_test_service(owner_id: int) -> Service:

    db = SessionLocal()

    try:
        service = Service(
            name=f"Test Service {uuid4()}",
            description="Test service description",
            price=100.00,
            duration_minutes=60,
            owner_id=owner_id,
        )

        db.add(service)
        db.commit()
        db.refresh(service)

        return service

    finally:
        db.close()


def get_auth_headers(user: User) -> dict[str, str]:

    token = create_access_token(str(user.id))

    return {
        "Authorization": f"Bearer {token}"
    }


def test_booking_confirmation_task_is_registered():

    assert (
        "app.tasks.notifications.send_booking_confirmation"
        in celery_app.tasks
    )


def test_booking_confirmation_task():

    result = send_booking_confirmation.apply(
        args=[101, "test@example.com"],
    )

    assert result.successful()
    assert result.result == (
        "Booking confirmation sent for booking 101"
    )


def test_booking_dispatches_confirmation_task():

    customer = create_test_user(UserRole.CUSTOMER)
    provider = create_test_user(UserRole.PROVIDER)

    service = create_test_service(provider.id)

    with patch(
        "app.api.routes.bookings.send_booking_confirmation.delay"
    ) as mock_delay:

        response = client.post(
            "/bookings",
            json={
                "service_id": service.id,
                "booking_date": "2030-01-01",
                "start_time": "10:00:00",
            },
            headers=get_auth_headers(customer),
        )

    assert response.status_code == 201

    booking = response.json()

    mock_delay.assert_called_once_with(
        booking["id"],
        customer.email,
    )
