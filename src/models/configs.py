from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Optional, Union

from pydantic import BaseModel, Field, model_validator

from __app_configs import (
    BaseConfigFields,
    PackageSizes,
    PricingImplementationTypes,
    PricingTypes,
    TransportTypes,
)
from __exceptions import (
    DatesError,
    InvalidConfigError,
    InvalidInputError,
    UnsupportedConfigError,
    UnsupportedFeeTypeError,
)
from models.grids import DiscountGrid, Grid, PeakOffPeakGrid, VolumeGrid


class BaseConfig(BaseModel):
    client_id: int = Field(gt=0)
    valid_from: datetime = Field(default=datetime.today() + timedelta(days=1))
    valid_to: Union[datetime, None] = Field(default=None)
    pricing_type: str = Field(default=PricingTypes.volume.value)
    config_type: str = Field(default=PricingImplementationTypes.fee.value)
    package_size_option: list[str] = Field(default=PackageSizes.list())
    transport_option: list[str] = Field(default=TransportTypes.list())

    @model_validator(mode="before")
    def validate_fee_config(cls, values: dict):
        pricing_type = values.get(BaseConfigFields.pricing_type.value)
        if pricing_type not in [
            PricingTypes.volume.value,
            PricingTypes.peak.value,
        ]:
            raise UnsupportedFeeTypeError(fee_type=pricing_type)

        valid_from = values.get(BaseConfigFields.valid_from.value)
        valid_to = values.get(BaseConfigFields.valid_to.value)

        if valid_to is not None and valid_to < valid_from:
            raise DatesError(valid_from=valid_from, valid_to=valid_to)

        package_size_option = values.get(BaseConfigFields.package_size_option.value)
        for pkg in package_size_option:
            if pkg not in PackageSizes.list():
                raise InvalidInputError(value=package_size_option)

        transport_option = values.get(BaseConfigFields.transport_option.value)
        for transport_type in transport_option:
            if transport_type not in TransportTypes.list():
                raise InvalidInputError(value=transport_option)

        validates_grids = Config._grids_validator(values=values)
        return validates_grids

    @staticmethod
    def _grids_validator(values: dict) -> dict:
        """This function validates that the correct Grid is mapped with
        correct pricing_type and config_type. The correct mappings are the following:
            - DiscountGrid, config_type = discount, pricing_type = volume_discount
            - VolumeGrid, config_type = fee, pricing_type = volume_discount
            - PeakOffPeakGrid, config_type = fee, pricing_type = peak_off_peak

        Args:
            values (Dict): values provided to initialise the Config object

        Raises:
            InvalidConfigError: error raised if incorrect mapping is identified

        Returns:
            Dict: validated values
        """
        pricing_type = values.get(BaseConfigFields.pricing_type.value)
        config_type = values.get(BaseConfigFields.config_type.value)

        # Check if Discounts are mapped with DiscountGrid
        if (
            config_type == PricingImplementationTypes.discount.value
            and pricing_type == PricingTypes.peak.value
        ):
            raise InvalidConfigError(config_type, pricing_type)

        return values

    def is_valid(self, timestamp: Optional[Union[datetime, str]] = None) -> bool:
        """Checks if config instance is valid at given timestamp (defaults to current date if not specified)."""
        if not timestamp:
            timestamp = datetime.now()
        if isinstance(timestamp, str):
            timestamp = datetime.strptime(timestamp, "%Y-%m-%d")
        return self.valid_from <= timestamp and (
            not self.valid_to or self.valid_to > timestamp
        )


class Config(BaseConfig):
    grids: list[Grid]

    @staticmethod
    def _create_grid(record: dict) -> Grid:
        """
        Args:
            record (Dict): data dictionary of the configuration elements

        Raises:
            UnsupportedConfigError: Exception if the unsupported configuration is identified

        Returns:
            Grid: correct Grid object based on the config_type, and scheme_type
        """
        if (
            record.get(BaseConfigFields.config_type.value)
            == PricingImplementationTypes.discount.value
        ):
            grid = DiscountGrid.from_brackets(brackets=json.loads(record["brackets"]))

        elif (
            record.get(BaseConfigFields.config_type.value)
            == PricingImplementationTypes.fee.value
            and record.get("scheme_type") == PricingTypes.volume.value
        ):
            grid = VolumeGrid.from_brackets(brackets=json.loads(record["brackets"]))

        elif (
            record.get(BaseConfigFields.config_type.value)
            == PricingImplementationTypes.fee.value
            and record.get("scheme_type") == PricingTypes.peak.value
        ):
            grid = PeakOffPeakGrid.from_brackets(
                brackets=json.loads(record["brackets"])
            )
        else:
            raise UnsupportedConfigError(
                grid_type=record.get("scheme_type"),
                config_type=record.get(BaseConfigFields.config_type.value),
            )
        return grid

    @classmethod
    def from_dict(cls, record: dict) -> Config:
        return Config(
            client_id=record[BaseConfigFields.client_id.value],
            valid_from=record[BaseConfigFields.valid_from.value],
            valid_to=record[BaseConfigFields.valid_to.value],
            pricing_type=record[BaseConfigFields.pricing_type.value],
            config_type=record[BaseConfigFields.config_type.value],
            grids=Config._create_grid(record=record),
        )


class ConfigReq(BaseConfig):
    package_size_option: str = Field(default=PackageSizes.to_string())
    transport_option: str = Field(default=TransportTypes.to_string())

    @model_validator(mode="before")
    def validate_fee_config(cls, values: dict):
        pricing_type = values.get(BaseConfigFields.pricing_type.value)
        if pricing_type not in [
            PricingTypes.volume.value,
            PricingTypes.peak.value,
        ]:
            raise UnsupportedFeeTypeError(fee_type=pricing_type)

        valid_from = values.get(BaseConfigFields.valid_from.value)
        valid_to = values.get(BaseConfigFields.valid_to.value)

        if valid_to is not None and valid_to < valid_from:
            raise DatesError(valid_from=valid_from, valid_to=valid_to)

        validates_grids = Config._grids_validator(values=values)
        return validates_grids
