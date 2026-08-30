from datetime import date, time
from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.security import create_access_token
from app.db.database import SessionLocal
from app.main import app
from app.models.booking import Booking, BookingStatus
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
            duration_minutes=45,
            owner_id=owner_id,
        )

        db.add(service)
        db.commit()
        db.refresh(service)

        return service

    finally:
        db.close()


def create_test_booking(
    customer_id: int,
    service_id: int,
    booking_date: date | None = None,
    start_time: time | None = None,
    status: BookingStatus = BookingStatus.PENDING,
) -> Booking:
    db = SessionLocal()

    try:
        booking = Booking(
            customer_id=customer_id,
            service_id=service_id,
            booking_date=booking_date or date(2026, 12, 1),
            start_time=start_time or time(10, 0),
            end_time=time(10, 45),
            status=status,
        )

        db.add(booking)
        db.commit()
        db.refresh(booking)

        return booking

    finally:
        db.close()


def test_customer_can_create_booking():

    customer = create_test_user(UserRole.CUSTOMER)
    provider = create_test_user(UserRole.PROVIDER)
    service = create_test_service(provider.id)

    response = client.post(
        "/bookings",
        headers=get_auth_headers(customer),
        json={
            "service_id": service.id,
            "booking_date": "2026-12-05",
            "start_time": "10:00:00",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["customer_id"] == customer.id
    assert data["service_id"] == service.id
    assert data["booking_date"] == "2026-12-05"
    assert data["start_time"] == "10:00:00"
    assert data["end_time"] == "10:45:00"
    assert data["status"] == "pending"


def test_provider_cannot_create_booking():

    provider = create_test_user(UserRole.PROVIDER)
    service = create_test_service(provider.id)

    response = client.post(
        "/bookings",
        headers=get_auth_headers(provider),
        json={
            "service_id": service.id,
            "booking_date": "2026-12-06",
            "start_time": "10:00:00",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "Only customers can create bookings"
    )


def test_booking_requires_authentication():

    response = client.post(
        "/bookings",
        json={
            "service_id": 1,
            "booking_date": "2026-12-07",
            "start_time": "10:00:00",
        },
    )

    assert response.status_code == 401

def test_booking_rejects_invalid_service_id():

    customer = create_test_user(UserRole.CUSTOMER)

    response = client.post(
        "/bookings",
        headers=get_auth_headers(customer),
        json={
            "service_id": 0,
            "booking_date": "2026-12-07",
            "start_time": "10:00:00",
        },
    )

    assert response.status_code == 422

def test_booking_rejects_negative_service_id():

    customer = create_test_user(UserRole.CUSTOMER)

    response = client.post(
        "/bookings",
        headers=get_auth_headers(customer),
        json={
            "service_id": -1,
            "booking_date": "2026-12-07",
            "start_time": "10:00:00",
        },
    )

    assert response.status_code == 422

def test_booking_nonexistent_service():

    customer = create_test_user(UserRole.CUSTOMER)

    response = client.post(
        "/bookings",
        headers=get_auth_headers(customer),
        json={
            "service_id": 999999,
            "booking_date": "2026-12-08",
            "start_time": "10:00:00",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Service not found"


def test_overlapping_booking_is_rejected():

    customer_one = create_test_user(UserRole.CUSTOMER)
    customer_two = create_test_user(UserRole.CUSTOMER)

    provider = create_test_user(UserRole.PROVIDER)
    service = create_test_service(provider.id)

    first_response = client.post(
        "/bookings",
        headers=get_auth_headers(customer_one),
        json={
            "service_id": service.id,
            "booking_date": "2026-12-10",
            "start_time": "10:00:00",
        },
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/bookings",
        headers=get_auth_headers(customer_two),
        json={
            "service_id": service.id,
            "booking_date": "2026-12-10",
            "start_time": "10:00:00",
        },
    )

    assert second_response.status_code == 400
    assert second_response.json()["detail"] == (
        "Service is already booked for this time"
    )


def test_provider_can_confirm_booking():

    customer = create_test_user(UserRole.CUSTOMER)
    provider = create_test_user(UserRole.PROVIDER)
    service = create_test_service(provider.id)

    booking = create_test_booking(
        customer.id,
        service.id,
    )

    response = client.patch(
        f"/bookings/{booking.id}/status",
        headers=get_auth_headers(provider),
        json={
            "status": "confirmed",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "confirmed"


def test_provider_can_complete_booking():

    customer = create_test_user(UserRole.CUSTOMER)
    provider = create_test_user(UserRole.PROVIDER)
    service = create_test_service(provider.id)

    booking = create_test_booking(
        customer.id,
        service.id,
        status=BookingStatus.CONFIRMED,
    )

    response = client.patch(
        f"/bookings/{booking.id}/status",
        headers=get_auth_headers(provider),
        json={
            "status": "completed",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "completed"


def test_completed_booking_cannot_be_cancelled():

    customer = create_test_user(UserRole.CUSTOMER)
    provider = create_test_user(UserRole.PROVIDER)
    service = create_test_service(provider.id)

    booking = create_test_booking(
        customer.id,
        service.id,
        status=BookingStatus.COMPLETED,
    )

    response = client.patch(
        f"/bookings/{booking.id}/status",
        headers=get_auth_headers(provider),
        json={
            "status": "cancelled",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Cannot change booking status from completed to cancelled"
    )


def test_customer_can_cancel_booking():

    customer = create_test_user(UserRole.CUSTOMER)
    provider = create_test_user(UserRole.PROVIDER)
    service = create_test_service(provider.id)

    booking = create_test_booking(
        customer.id,
        service.id,
    )

    response = client.patch(
        f"/bookings/{booking.id}/status",
        headers=get_auth_headers(customer),
        json={
            "status": "cancelled",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"


def test_customer_cannot_confirm_booking():

    customer = create_test_user(UserRole.CUSTOMER)
    provider = create_test_user(UserRole.PROVIDER)
    service = create_test_service(provider.id)

    booking = create_test_booking(
        customer.id,
        service.id,
    )

    response = client.patch(
        f"/bookings/{booking.id}/status",
        headers=get_auth_headers(customer),
        json={
            "status": "confirmed",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "Customers can only cancel bookings"
    )


def test_provider_can_cancel_booking():

    customer = create_test_user(UserRole.CUSTOMER)
    provider = create_test_user(UserRole.PROVIDER)
    service = create_test_service(provider.id)

    booking = create_test_booking(
        customer.id,
        service.id,
    )

    response = client.patch(
        f"/bookings/{booking.id}/status",
        headers=get_auth_headers(provider),
        json={
            "status": "cancelled",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"


def test_admin_can_change_booking_status():

    customer = create_test_user(UserRole.CUSTOMER)
    provider = create_test_user(UserRole.PROVIDER)
    admin = create_test_user(UserRole.ADMIN)

    service = create_test_service(provider.id)

    booking = create_test_booking(
        customer.id,
        service.id,
    )

    response = client.patch(
        f"/bookings/{booking.id}/status",
        headers=get_auth_headers(admin),
        json={
            "status": "confirmed",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "confirmed"
