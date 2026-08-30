import json

from fastapi import APIRouter, Depends, HTTPException, status
from redis.asyncio import Redis
from redis.exceptions import RedisError
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.redis import get_redis
from app.core.cache import (
    SERVICES_LIST_CACHE_KEY,
    invalidate_services_cache,
)
from app.db.dependencies import get_db
from app.models.user import User, UserRole
from app.schemas.service import (
    ServiceCreate,
    ServiceResponse,
    ServiceUpdate,
)
from app.services.service import (
    create_service,
    delete_service,
    get_service,
    get_services,
    update_service,
)


router = APIRouter(
    prefix="/services",
    tags=["Services"],
)


@router.post(
    "",
    response_model=ServiceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_service_endpoint(
    service_data: ServiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    redis: Redis = Depends(get_redis),
):
    if current_user.role not in {
        UserRole.PROVIDER,
        UserRole.ADMIN,
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only providers and admins can create services",
        )

    service = create_service(
        db,
        service_data,
        current_user.id,
    )

    await invalidate_services_cache(redis)

    return service

@router.get(
    "",
    response_model=list[ServiceResponse],
)
async def list_services(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    redis: Redis = Depends(get_redis),
):
    try:
        cached_services = await redis.get(SERVICES_LIST_CACHE_KEY)

        if cached_services:
            return json.loads(cached_services)

    except RedisError:
        pass

    services = get_services(db)

    try:
        serialized_services = [
            ServiceResponse.model_validate(service).model_dump(mode="json")
            for service in services
        ]

        await redis.set(
            SERVICES_LIST_CACHE_KEY,
            json.dumps(serialized_services),
            ex=60,
        )

    except RedisError:
        pass

    return services

@router.get(
    "/{service_id}",
    response_model=ServiceResponse,
)
def get_service_endpoint(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = get_service(db, service_id)

    if service is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found",
        )

    return service

@router.patch(
    "/{service_id}",
    response_model=ServiceResponse,
)
async def update_service_endpoint(
    service_id: int,
    service_data: ServiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    redis: Redis = Depends(get_redis),
):
    service = get_service(db, service_id)

    if service is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found",
        )

    if (
        current_user.role != UserRole.ADMIN
        and service.owner_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this service",
        )

    updated_service = update_service(
        db,
        service,
        service_data,
    )

    await invalidate_services_cache(redis)

    return updated_service

@router.delete(
    "/{service_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_service_endpoint(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    redis: Redis = Depends(get_redis),
):
    service = get_service(db, service_id)

    if service is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found",
        )

    if (
        current_user.role != UserRole.ADMIN
        and service.owner_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this service",
        )

    delete_service(db, service)

    await invalidate_services_cache(redis)
