from datetime import date, time, datetime

from pydantic import BaseModel, ConfigDict

from app.models.booking import BookingStatus


class BookingCreate(BaseModel):
    service_id: int
    booking_date: date
    start_time: time


class BookingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int
    service_id: int
    booking_date: date
    start_time: time
    end_time: time
    status: BookingStatus
    created_at: datetime
    updated_at: datetime


class BookingStatusUpdate(BaseModel):
    status: BookingStatus
