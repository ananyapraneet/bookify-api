import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError

from app.api.routes.auth import router as auth_router
from app.api.routes.bookings import router as bookings_router
from app.api.routes.health import router as health_router
from app.api.routes.roles import router as roles_router
from app.api.routes.services import router as services_router
from app.core.exceptions import (
    general_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from app.core.logging import configure_logging

configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup")

    yield

    logger.info("Application shutdown")


app = FastAPI(
    title="Bookify API",
    description="Production-ready service booking platform",
    version="1.0.0",
    lifespan=lifespan,
)

logger.info("Bookify API initialized")

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
app.include_router(health_router)


@app.get("/")
def root():
    return {"message": "Bookify API is running"}
