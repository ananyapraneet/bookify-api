from app.core.celery import celery_app


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
    max_retries=3,
)
def send_booking_confirmation(
    self,
    booking_id: int,
    customer_email: str,
) -> str:

    print(f"Sending booking confirmation for booking {booking_id} to {customer_email}")

    return f"Booking confirmation sent for booking {booking_id}"
