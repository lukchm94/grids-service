from datetime import datetime, timedelta

from pydantic import BaseModel, Field, model_validator

from __exceptions import DatesError


class AcctVol(BaseModel):
    account_id: int = Field(gt=0, default=1)
    date: datetime = Field(default=datetime.now().date())
    volume: int = Field(gt=0, default=0)


class AcctVolResp(BaseModel):
    account_id: int = Field(gt=0, default=1)
    total_vol: int = Field(gt=0, default=0)
    date_start: datetime = Field(default=datetime.now().date())
    date_end: datetime = Field(default=datetime.now().date() + timedelta(days=1))

    @model_validator(mode="before")
    def validate_config(cls, values: dict):
        date_start = values.get("date_start")
        date_end = values.get("date_end")

        if date_end is not None and date_end < date_start:
            raise DatesError(date_start, date_end)

        return values
