from __future__ import annotations

from typing import Union

from pydantic import BaseModel, Field, model_validator

from __app_configs import AppVars
from __exceptions import HoursError, InvalidDayError, InvalidInputError


class Grid(BaseModel):
    min_volume_threshold: int = Field(gt=0)
    max_volume_threshold: Union[int, None]
    min_distance_in_unit: float = Field(ge=0)
    max_distance_in_unit: Union[float, None]

    @model_validator(mode="before")
    def validate_grid(cls, values: dict):
        if isinstance(values, DiscountGrid):
            values = values.model_dump()
        min_volume_threshold = values.get("min_volume_threshold")
        max_volume_threshold = values.get("max_volume_threshold")

        if (
            max_volume_threshold is not None
            and max_volume_threshold <= min_volume_threshold
        ):
            raise InvalidInputError(value=max_volume_threshold)

        min_distance_in_unit = values.get("min_distance_in_unit")
        max_distance_in_unit = values.get("max_distance_in_unit")

        if (
            max_distance_in_unit is not None
            and max_distance_in_unit <= min_distance_in_unit
        ):
            raise InvalidInputError(value=max_distance_in_unit)

        return values


class VolumeGrid(Grid):
    pickup_amount: int = Field(ge=0)
    distance_amount_per_unit: int = Field(ge=0)
    dropoff_amount: int = Field(ge=0)


class VolumeGridReq(VolumeGrid):
    config_id: int = Field(gt=0)


class DiscountGrid(Grid):
    discount_amount: int = Field(lt=0)


class DiscountGridReq(DiscountGrid):
    config_id: int = Field(gt=0)


class PeakOffPeakGrid(VolumeGrid):
    weekday_option: list[int]
    hour_start: int = Field(ge=0, lt=24)
    hour_end: int = Field(gt=0, le=24)

    @model_validator(mode="before")
    def validate_peak_grid(cls, values: dict):
        if isinstance(values, DiscountGrid):
            return values.model_dump()
        min_volume_threshold = values.get("min_volume_threshold")
        max_volume_threshold = values.get("max_volume_threshold")

        if (
            max_volume_threshold is not None
            and max_volume_threshold <= min_volume_threshold
        ):
            raise InvalidInputError(value=max_volume_threshold)

        min_distance_in_unit = values.get("min_distance_in_unit")
        max_distance_in_unit = values.get("max_distance_in_unit")

        if (
            max_distance_in_unit is not None
            and max_distance_in_unit <= min_distance_in_unit
        ):
            raise InvalidInputError(value=max_distance_in_unit)

        weekday_option = values.get("weekday_option")
        for day in weekday_option:
            if not 0 <= day < 7:
                raise InvalidDayError(day=day)

        hour_start = values.get("hour_start")
        hour_end = values.get("hour_end")
        if hour_start >= hour_end:
            raise HoursError()

        return values


class PeakGridReq(PeakOffPeakGrid):
    config_id: int = Field(gt=0)
    weekday_option: str = Field(default=AppVars.weekend_days.value)

    @model_validator(mode="before")
    def validate_peak_grid(cls, values: dict):
        min_volume_threshold = values.get("min_volume_threshold")
        max_volume_threshold = values.get("max_volume_threshold")

        if (
            max_volume_threshold is not None
            and max_volume_threshold <= min_volume_threshold
        ):
            raise InvalidInputError(value=max_volume_threshold)

        min_distance_in_unit = values.get("min_distance_in_unit")
        max_distance_in_unit = values.get("max_distance_in_unit")

        if (
            max_distance_in_unit is not None
            and max_distance_in_unit <= min_distance_in_unit
        ):
            raise InvalidInputError(value=max_distance_in_unit)

        hour_start = values.get("hour_start")
        hour_end = values.get("hour_end")
        if hour_start >= hour_end:
            raise HoursError()

        return values
