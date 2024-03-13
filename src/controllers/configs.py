from __future__ import annotations

from logging import Logger
from typing import Union

from __app_configs import Deliminator, LogMsg, PricingImplementationTypes, PricingTypes
from __exceptions import (
    ClientIdConfigError,
    ConfigGridValidationError,
    UnsupportedConfigAfterUpdateError,
)
from database.main import db_dependency
from database.models import (
    ConfigTable,
    DiscountGridTable,
    PeakGridTable,
    VolumeGridTable,
)
from models.configs import BaseConfig, ConfigReq, ConfigResp
from models.grids import DiscountGrid, PeakOffPeakGrid, VolumeGrid


class ConfigReqController:
    config_req: BaseConfig

    def __init__(self, config_req: BaseConfig) -> ConfigReqController:
        self.config_req = config_req

    def format(self) -> ConfigReq:
        return ConfigReq(
            client_id=self.config_req.client_id,
            valid_from=self.config_req.valid_from,
            valid_to=self.config_req.valid_to,
            pricing_type=self.config_req.pricing_type,
            config_type=self.config_req.config_type,
            package_size_option=Deliminator.comma.value.join(
                [package for package in self.config_req.package_size_option]
            ),
            transport_option=Deliminator.comma.value.join(
                [transport for transport in self.config_req.transport_option]
            ),
        )

    def check_if_exists(self, db: db_dependency) -> bool:
        config_to_create = (
            db.query(ConfigTable)
            .filter(ConfigTable.client_id == self.config_req.client_id)
            .order_by(ConfigTable.valid_to)
            .first()
        )
        return True if config_to_create is not None else False


class ConfigModelController:
    config_model: ConfigTable

    def __init__(self, config_model: ConfigTable) -> ConfigModelController:
        self.config_model: ConfigTable = config_model

    def update(self, config_req: ConfigReq) -> ConfigTable:
        updated_config: ConfigTable = self.config_model
        if updated_config.client_id != config_req.client_id:
            raise ClientIdConfigError()
        updated_config.client_id = config_req.client_id
        updated_config.valid_from = config_req.valid_from
        updated_config.valid_to = config_req.valid_to
        updated_config.pricing_type = config_req.pricing_type
        updated_config.config_type = config_req.config_type
        updated_config.package_size_option = config_req.package_size_option
        updated_config.transport_option = config_req.transport_option

        return updated_config

    def expire(self, config_req: ConfigReq, db: db_dependency, logger: Logger) -> None:
        config_to_expire: ConfigTable = self.config_model
        if config_to_expire.client_id != config_req.client_id:
            raise ClientIdConfigError()

        config_to_expire.valid_to = config_req.valid_from
        db.add(config_to_expire)
        db.commit()
        logger.info(
            LogMsg.config_expired.value.format(
                config_id=config_to_expire.id,
                client_id=config_to_expire.client_id,
                expire_date=config_to_expire.valid_to,
            )
        )


class ConfigRespController:
    config_id: int
    db: db_dependency

    def __init__(self, config_id: int, db: db_dependency) -> ConfigRespController:
        self.config_id = config_id
        self.db = db

    def _get_volume_grids(self) -> list[VolumeGrid]:
        return [
            grid.to_grid()
            for grid in (
                self.db.query(VolumeGridTable)
                .filter(VolumeGridTable.config_id == self.config_id)
                .all()
            )
        ]

    def _get_peak_grids(self) -> list[PeakOffPeakGrid]:
        return [
            grid.to_grid()
            for grid in (
                self.db.query(PeakGridTable)
                .filter(PeakGridTable.config_id == self.config_id)
                .all()
            )
        ]

    def _get_discounts_grids(self) -> list[DiscountGrid]:
        return [
            grid.to_grid()
            for grid in (
                self.db.query(DiscountGridTable)
                .filter(DiscountGridTable.config_id == self.config_id)
                .all()
            )
        ]

    def check_grids(self, config_model: Union[ConfigReq, ConfigTable]) -> None:
        if (
            config_model.config_type == PricingImplementationTypes.discount.value
            and config_model.pricing_type == PricingTypes.volume.value
            and (len(self._get_peak_grids()) > 0 or len(self._get_volume_grids()) > 0)
        ):
            raise UnsupportedConfigAfterUpdateError()

        elif (
            config_model.config_type == PricingImplementationTypes.fee.value
            and config_model.pricing_type == PricingTypes.peak.value
            and (
                len(self._get_discounts_grids()) > 0
                or len(self._get_volume_grids()) > 0
            )
        ):
            raise UnsupportedConfigAfterUpdateError()

        elif (
            config_model.config_type == PricingImplementationTypes.fee.value
            and config_model.pricing_type == PricingTypes.volume.value
            and (
                len(self._get_discounts_grids()) > 0 or len(self._get_peak_grids()) > 0
            )
        ):
            raise UnsupportedConfigAfterUpdateError()

    def get_config(self, config_model: BaseConfig) -> ConfigResp:
        if (
            config_model.config_type == PricingImplementationTypes.discount.value
            and config_model.pricing_type == PricingTypes.volume.value
        ):
            return ConfigResp(
                client_id=config_model.client_id,
                valid_from=config_model.valid_from,
                valid_to=config_model.valid_to,
                pricing_type=config_model.pricing_type,
                config_type=config_model.config_type,
                package_size_option=config_model.package_size_option,
                transport_option=config_model.transport_option,
                grids=self._get_discounts_grids(),
            )

        elif (
            config_model.config_type == PricingImplementationTypes.fee.value
            and config_model.pricing_type == PricingTypes.peak.value
        ):
            return ConfigResp(
                client_id=config_model.client_id,
                valid_from=config_model.valid_from,
                valid_to=config_model.valid_to,
                pricing_type=config_model.pricing_type,
                config_type=config_model.config_type,
                package_size_option=config_model.package_size_option,
                transport_option=config_model.transport_option,
                grids=self._get_peak_grids(),
            )

        elif (
            config_model.config_type == PricingImplementationTypes.fee.value
            and config_model.pricing_type == PricingTypes.volume.value
        ):
            return ConfigResp(
                client_id=config_model.client_id,
                valid_from=config_model.valid_from,
                valid_to=config_model.valid_to,
                pricing_type=config_model.pricing_type,
                config_type=config_model.config_type,
                package_size_option=config_model.package_size_option,
                transport_option=config_model.transport_option,
                grids=self._get_volume_grids(),
            )

        raise ConfigGridValidationError()
