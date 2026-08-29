from datetime import date, time, datetime, timezone
from enum import Enum

from sqlalchemy import Date, DateTime, Enum as SQLEnum, ForeignKey, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True)

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    service_id: Mapped[int] = mapped_column(
        ForeignKey("services.id"),
        nullable=False,
        index=True,
    )

    booking_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    start_time: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )

    end_time: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )

    status: Mapped[BookingStatus] = mapped_column(
    	SQLEnum(
            BookingStatus,
            values_callable=lambda enum_class: [
            member.value for member in enum_class
            ],
    	),
    	nullable=False,
    	default=BookingStatus.PENDING,
    )

    created_at: Mapped[datetime] = mapped_column(
    	DateTime,
    	default=lambda: datetime.now(timezone.utc),
    	nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
    	DateTime,
    	default=lambda: datetime.now(timezone.utc),
    	onupdate=lambda: datetime.now(timezone.utc),
    	nullable=False,
    )

    customer: Mapped["User"] = relationship(
        "User",
        back_populates="bookings",
    )

    service: Mapped["Service"] = relationship(
        "Service",
        back_populates="bookings",
    )
