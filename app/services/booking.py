from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.booking import Booking, BookingStatus
from app.models.service import Service
from app.models.user import UserRole
from app.schemas.booking import BookingCreate


def create_booking(
    db: Session,
    booking_data: BookingCreate,
    customer_id: int,
) -> Booking:

    service = db.scalar(select(Service).where(Service.id == booking_data.service_id))

    if service is None:
        raise ValueError("Service not found")

    if service.owner_id == customer_id:
        raise ValueError("You cannot book your own service")

    start_datetime = datetime.combine(
        booking_data.booking_date,
        booking_data.start_time,
    )

    end_datetime = start_datetime + timedelta(minutes=service.duration_minutes)

    existing_booking = db.scalar(
        select(Booking).where(
            Booking.service_id == service.id,
            Booking.booking_date == booking_data.booking_date,
            Booking.status.in_(
                [
                    BookingStatus.PENDING,
                    BookingStatus.CONFIRMED,
                ]
            ),
            Booking.start_time < end_datetime.time(),
            Booking.end_time > booking_data.start_time,
        )
    )

    if existing_booking is not None:
        raise ValueError("Service is already booked for this time")

    booking = Booking(
        customer_id=customer_id,
        service_id=service.id,
        booking_date=booking_data.booking_date,
        start_time=booking_data.start_time,
        end_time=end_datetime.time(),
        status=BookingStatus.PENDING,
    )

    db.add(booking)
    db.commit()
    db.refresh(booking)

    return booking


def get_bookings(
    db: Session,
    current_user_id: int,
    current_user_role,
) -> list[Booking]:

    query = select(Booking)

    if current_user_role == UserRole.CUSTOMER:
        query = query.where(Booking.customer_id == current_user_id)

    elif current_user_role == UserRole.PROVIDER:
        query = query.join(
            Service,
            Booking.service_id == Service.id,
        ).where(Service.owner_id == current_user_id)

    return list(db.scalars(query).all())


def get_booking(
    db: Session,
    booking_id: int,
) -> Booking | None:

    return db.scalar(select(Booking).where(Booking.id == booking_id))


def update_booking_status(
    db: Session,
    booking: Booking,
    new_status: BookingStatus,
) -> Booking:

    current_status = booking.status

    allowed_transitions = {
        BookingStatus.PENDING: {
            BookingStatus.CONFIRMED,
            BookingStatus.CANCELLED,
        },
        BookingStatus.CONFIRMED: {
            BookingStatus.COMPLETED,
            BookingStatus.CANCELLED,
        },
        BookingStatus.COMPLETED: set(),
        BookingStatus.CANCELLED: set(),
    }

    if new_status not in allowed_transitions[current_status]:
        raise ValueError(
            f"Cannot change booking status from "
            f"{current_status.value} to {new_status.value}"
        )

    booking.status = new_status

    db.commit()
    db.refresh(booking)

    return booking
