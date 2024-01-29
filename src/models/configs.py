from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Optional, Union

from pydantic import BaseModel, Field, model_validator

from __app_configs import (
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


class Config(BaseModel):
    client_id: int = Field(gt=0)
    valid_from: datetime = Field(default=datetime.today().date() + timedelta(days=1))
    valid_to: Union[datetime, None] = Field(default=None)
    pricing_type: str
    config_type: str
    package_size_option: list[str] = Field(default=PackageSizes.list())
    transport_option: list[str] = Field(default=TransportTypes.list())
    grids: list[Grid]

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
        grids = values.get("grids")
        pricing_type = values.get("pricing_type")
        config_type = values.get("config_type")

        # Check if Discounts are mapped with DiscountGrid
        if config_type == PricingImplementationTypes.discount.value:
            if not all([isinstance(grid, DiscountGrid) for grid in grids]):
                raise InvalidConfigError(
                    config=config_type,
                    pricing=pricing_type,
                    grid=[type(grid).__name__ for grid in grids],
                )

        elif config_type == PricingImplementationTypes.fee.value:
            # Check if Volume Fees are mapped with VolumeGrid
            if pricing_type == PricingTypes.volume.value and not all(
                [isinstance(grid, VolumeGrid) for grid in grids]
            ):
                raise InvalidConfigError(
                    config=config_type,
                    pricing=pricing_type,
                    grid=[type(grid).__name__ for grid in grids],
                )

            # Check if PeakOffPeak Fees are mapped with PeakOffPeakGrid
            elif pricing_type == PricingTypes.peak.value and not all(
                [isinstance(grid, PeakOffPeakGrid) for grid in grids]
            ):
                raise InvalidConfigError(
                    config=config_type,
                    pricing=pricing_type,
                    grid=[type(grid).__name__ for grid in grids],
                )

        else:
            raise InvalidInputError(value=config_type)
        return values

    @model_validator(mode="before")
    def validate_fee_config(cls, values: dict):
        pricing_type = values.get("pricing_type")
        if pricing_type not in [
            PricingTypes.volume.value,
            PricingTypes.peak.value,
        ]:
            raise UnsupportedFeeTypeError(fee_type=pricing_type)

        valid_from = values.get("valid_from")
        valid_to = values.get("valid_to")

        if valid_to is not None and valid_to < valid_from:
            raise DatesError(valid_from=valid_from, valid_to=valid_to)

        package_size_option = values.get("package_size_option")
        for pkg in package_size_option:
            if pkg not in PackageSizes.list():
                raise InvalidInputError(value=package_size_option)

        transport_option = values.get("transport_option")
        for transport_type in transport_option:
            if transport_type not in TransportTypes.list():
                raise InvalidInputError(value=transport_option)

        validates_grids = Config._grids_validator(values=values)
        return validates_grids

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
        if record.get("config_type") == PricingImplementationTypes.discount.value:
            grid = DiscountGrid.from_brackets(brackets=json.loads(record["brackets"]))

        elif (
            record.get("config_type") == PricingImplementationTypes.fee.value
            and record.get("scheme_type") == PricingTypes.volume.value
        ):
            grid = VolumeGrid.from_brackets(brackets=json.loads(record["brackets"]))

        elif (
            record.get("config_type") == PricingImplementationTypes.fee.value
            and record.get("scheme_type") == PricingTypes.peak.value
        ):
            grid = PeakOffPeakGrid.from_brackets(
                brackets=json.loads(record["brackets"])
            )
        else:
            raise UnsupportedConfigError(
                grid_type=record.get("scheme_type"),
                config_type=record.get("config_type"),
            )
        return grid

    @classmethod
    def from_dict(cls, record: dict) -> Config:
        return Config(
            client_id=record["client_id"],
            valid_from=record["valid_from_date"],
            valid_to=record["valid_to_date"],
            pricing_type=record["pricing_type"],
            config_type=record["config_type"],
            grids=Config._create_grid(record=record),
        )

    def is_valid(self, timestamp: Optional[Union[datetime, str]] = None) -> bool:
        """Checks if config instance is valid at given timestamp (defaults to current date if not specified)."""
        if not timestamp:
            timestamp = datetime.now()
        if isinstance(timestamp, str):
            timestamp = datetime.strptime(timestamp, "%Y-%m-%d")
        return self.valid_from <= timestamp and (
            not self.valid_to or self.valid_to > timestamp
        )
