from decimal import Decimal
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

class ServiceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    price: Decimal = Field(gt=0, decimal_places=2)
    duration_minutes: int = Field(gt=0)
    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Service name cannot be empty")

        return value

class ServiceUpdate(BaseModel):

    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    price: Decimal | None = Field(default=None, gt=0, decimal_places=2)
    duration_minutes: int | None = Field(default=None, gt=0)
    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()
        if not value:
            raise ValueError("Service name cannot be empty")

        return value

class ServiceResponse(BaseModel):
    id: int
    name: str
    description: str | None
    price: Decimal
    duration_minutes: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
