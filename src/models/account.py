from __future__ import annotations

from datetime import datetime, timedelta
from typing import Union

from pydantic import BaseModel, Field, model_validator

from __app_configs import AccountFields, Defaults
from __exceptions import DatesError


class AccountBaseReq(BaseModel):
    client_ids: list[int] = Field(default=Defaults.client_ids_example.value)
    client_group_name: Union[str, None] = Field(
        default=Defaults.group_name_example.value
    )
    valid_from: datetime = Field(default=datetime.today() + timedelta(days=1))
    valid_to: Union[None, datetime] = Field(default=None)
    deleted_at: Union[None, datetime] = Field(default=None)

    @model_validator(mode="before")
    def validate_config(cls, values: dict):
        valid_from = values.get(AccountFields.valid_from.value)
        valid_to = values.get(AccountFields.valid_to.value)
        if valid_to is not None and valid_to < valid_from:
            raise DatesError(valid_from=valid_from, valid_to=valid_to)
        return values


class AccountReq(AccountBaseReq):
    client_ids: str


class Account(AccountBaseReq):
    account_id: int = Field(gt=0, default=1)
