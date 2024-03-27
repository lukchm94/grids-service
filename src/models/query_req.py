from datetime import datetime, timedelta

from pydantic import BaseModel, Field, model_validator

from __app_configs import QueryFields
from __exceptions import DatesError


class DatesReq(BaseModel):
    start: datetime = Field(default=datetime.now())
    end: datetime = Field(default=datetime.now() + timedelta(days=1))

    @model_validator(mode="before")
    def validate_req(cls, values: dict):
        date_start: datetime = values.get(QueryFields.start.value)
        date_end: datetime = values.get(QueryFields.end.value)
        if date_end < date_start:
            raise DatesError(valid_from=date_start, valid_to=date_end)

        return values

    def to_str(self) -> str:
        return f"{self.start.date()} - {self.end.date()}"
