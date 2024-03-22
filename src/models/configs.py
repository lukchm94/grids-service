from __future__ import annotations

from datetime import datetime, timedelta
from typing import Union

from pydantic import BaseModel, Field, model_validator

from __app_configs import (
    BaseConfigFields,
    ConfigField,
    Defaults,
    Frequency,
    Groups,
    PackageSizes,
    PricingImplementationTypes,
    PricingTypes,
    TransportTypes,
)
from __exceptions import (
    DatesError,
    GridReqConversionError,
    InvalidConfigError,
    InvalidInputError,
    UnsupportedFeeTypeError,
)
from models.grids import (
    DiscountGrid,
    DiscountGridReq,
    PeakGridReq,
    PeakOffPeakGrid,
    VolumeGrid,
    VolumeGridReq,
)


class BaseConfig(BaseModel):
    valid_from: datetime = Field(default=datetime.today() + timedelta(days=1))
    valid_to: datetime = Field(
        default=datetime.today() + timedelta(days=Defaults.expiration.value)
    )
    pricing_type: str = Field(default=PricingTypes.volume.value)
    config_type: str = Field(default=PricingImplementationTypes.fee.value)
    group: str = Field(default=Groups.individual.value)
    package_size_option: list[str] = Field(default=PackageSizes.list())
    transport_option: list[str] = Field(default=TransportTypes.list())
    frequency: str = Field(default=Frequency.week.value)
    deleted_at: Union[None, datetime] = Field(default=None)

    @model_validator(mode="before")
    def validate_config(cls, values: dict):
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

        group_option = values.get(BaseConfigFields.group.value)
        if group_option not in Groups.list():
            raise InvalidInputError(value=group_option)

        package_size_option = values.get(BaseConfigFields.package_size_option.value)
        for pkg in package_size_option:
            if pkg not in PackageSizes.list():
                raise InvalidInputError(value=package_size_option)

        transport_option = values.get(BaseConfigFields.transport_option.value)
        for transport_type in transport_option:
            if transport_type not in TransportTypes.list():
                raise InvalidInputError(value=transport_option)

        freq_option = values.get(BaseConfigFields.freq.value)
        if freq_option not in Frequency.list():
            raise InvalidInputError(value=freq_option)

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


class BaseConfigResp(BaseConfig):
    account_id: int = Field(gt=0, default=1)


class ConfigReq(BaseConfig):
    account_id: int = Field(gt=0, default=1)
    package_size_option: str = Field(default=PackageSizes.to_string())
    transport_option: str = Field(default=TransportTypes.to_string())

    @model_validator(mode="before")
    def validate_config(cls, values: dict):
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

        group_option = values.get(BaseConfigFields.group.value)
        if group_option not in Groups.list():
            raise InvalidInputError(value=group_option)

        freq_option = values.get(BaseConfigFields.freq.value)
        if freq_option not in Frequency.list():
            raise InvalidInputError(value=freq_option)

        validates_grids = BaseConfig._grids_validator(values=values)

        return validates_grids


class Config(BaseConfig):
    grids: Union[list[VolumeGrid], list[PeakOffPeakGrid], list[DiscountGrid]]

    @model_validator(mode="before")
    def validate_grids(cls, values: dict):
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

        values[ConfigField.grids.value] = Config._convert_grids(values)
        for grid in values.get(ConfigField.grids.value):
            if not isinstance(grid, (VolumeGrid, PeakOffPeakGrid, DiscountGrid)):
                raise GridReqConversionError()

        validates_grids = BaseConfig._grids_validator(values=values)
        return validates_grids

    @staticmethod
    def _convert_grids(
        values: dict,
    ) -> Union[list[DiscountGrid, VolumeGrid, PeakOffPeakGrid]]:
        if (
            values.get(BaseConfigFields.config_type.value)
            == PricingImplementationTypes.fee.value
            and values.get(BaseConfigFields.pricing_type.value)
            == PricingTypes.peak.value
        ):
            return [
                PeakOffPeakGrid(**grid) for grid in values.get(ConfigField.grids.value)
            ]

        elif (
            values.get(BaseConfigFields.config_type.value)
            == PricingImplementationTypes.fee.value
            and values.get(BaseConfigFields.pricing_type.value)
            == PricingTypes.volume.value
        ):
            return [VolumeGrid(**grid) for grid in values.get(ConfigField.grids.value)]
        elif (
            values.get(BaseConfigFields.config_type.value)
            == PricingImplementationTypes.discount.value
            and values.get(BaseConfigFields.pricing_type.value)
            == PricingTypes.volume.value
        ):
            return [
                DiscountGrid(**grid) for grid in values.get(ConfigField.grids.value)
            ]


class ConfigResp(BaseConfigResp):
    grids: Union[list[VolumeGrid], list[PeakOffPeakGrid], list[DiscountGrid]]


class ConfigGridReq(ConfigReq):
    grids: Union[list[VolumeGridReq], list[PeakGridReq], list[DiscountGridReq]]
