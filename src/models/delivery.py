from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from __app_configs import DeliveryStatus
from __exceptions import InvalidStatusError


class Delivery(BaseModel):
    id: int = Field(gt=0)
    client_id: int = Field(gt=0)
    status: str = Field(default="")
    created_at: datetime = Field(default=datetime.now())

    @model_validator(mode="before")
    def validate_grid(cls, values: dict) -> dict:
        status = values.get("status")

        if status not in DeliveryStatus.list():
            raise InvalidStatusError(status=status)

        return values
