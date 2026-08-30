from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError

from app.api.routes.auth import router as auth_router
from app.api.routes.roles import router as roles_router
from app.api.routes.services import router as services_router
from app.api.routes.bookings import router as bookings_router

from app.core.exceptions import (
    general_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)

app = FastAPI(
    title="Bookify API",
    description="Production-ready service booking platform",
    version="1.0.0",
)

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler,
)
app.add_exception_handler(Exception, general_exception_handler)

app.include_router(auth_router)
app.include_router(roles_router)
app.include_router(services_router)
app.include_router(bookings_router)


@app.get("/")
def root():
    return {
        "message": "Bookify API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }
