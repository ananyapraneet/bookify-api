from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.service import Service
from app.schemas.service import ServiceCreate, ServiceUpdate


def create_service(
    db: Session,
    service_data: ServiceCreate,
    owner_id: int,
) -> Service:
    service = Service(
        name=service_data.name,
        description=service_data.description,
        price=service_data.price,
        duration_minutes=service_data.duration_minutes,
        owner_id=owner_id,
    )

    db.add(service)
    db.commit()
    db.refresh(service)

    return service


def get_service(
    db: Session,
    service_id: int,
) -> Service | None:
    statement = select(Service).where(Service.id == service_id)

    return db.scalar(statement)


def get_services(
    db: Session,
) -> list[Service]:
    statement = select(Service).order_by(Service.id)

    return list(db.scalars(statement).all())


def get_services_by_owner(
    db: Session,
    owner_id: int,
) -> list[Service]:
    statement = select(Service).where(Service.owner_id == owner_id).order_by(Service.id)

    return list(db.scalars(statement).all())


def update_service(
    db: Session,
    service: Service,
    service_data: ServiceUpdate,
) -> Service:
    update_data = service_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(service, field, value)

    db.commit()
    db.refresh(service)

    return service


def delete_service(
    db: Session,
    service: Service,
) -> None:
    db.delete(service)
    db.commit()
