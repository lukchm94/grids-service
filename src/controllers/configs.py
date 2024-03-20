from datetime import datetime
from logging import Logger
from typing import Union

from fastapi import Response, status
from sqlalchemy import desc

from __app_configs import (
    AppVars,
    Deliminator,
    LogMsg,
    PricingImplementationTypes,
    PricingTypes,
)
from __exceptions import ClientIdConfigError, UnsupportedConfigAfterUpdateError
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

    def __init__(self, config_req: BaseConfig) -> None:
        self.config_req = config_req

    def format(self) -> ConfigReq:
        return ConfigReq(
            client_id=self.config_req.client_id,
            valid_from=self.config_req.valid_from,
            valid_to=self.config_req.valid_to,
            pricing_type=self.config_req.pricing_type,
            config_type=self.config_req.config_type,
            group=self.config_req.group,
            package_size_option=Deliminator.comma.value.join(
                [package for package in self.config_req.package_size_option]
            ),
            transport_option=Deliminator.comma.value.join(
                [transport for transport in self.config_req.transport_option]
            ),
            frequency=self.config_req.frequency,
            deleted_at=None,
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

    def __init__(self, config_model: ConfigTable) -> None:
        self.config_model: ConfigTable = config_model

    def update(self, config_req: ConfigReq) -> ConfigTable:
        updated_config: ConfigTable = self.config_model
        if updated_config.client_id != config_req.client_id:
            raise ClientIdConfigError(updated_config.client_id, config_req.client_id)
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
            raise ClientIdConfigError(config_to_expire.client_id, config_req.client_id)

        config_to_expire.valid_to = config_req.valid_from
        if config_to_expire.valid_from >= config_to_expire.valid_to:
            config_to_expire.valid_from = config_to_expire.valid_to

        db.add(config_to_expire)
        db.commit()
        logger.info(
            LogMsg.config_expired.value.format(
                config_id=config_to_expire.id,
                client_id=config_to_expire.client_id,
                expire_date=config_to_expire.valid_to,
                expire_from=config_to_expire.valid_from,
            )
        )


class ConfigRespController:
    config_id: int
    db: db_dependency
    logger: Logger

    def __init__(self, config_id: int, db: db_dependency, logger: Logger) -> None:
        self.config_id = config_id
        self.db = db
        self.logger = logger

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
            self.logger.warn(
                LogMsg.unsupported_config_grid.format(
                    grid=config_model.pricing_type.upper(),
                    config=config_model.config_type.upper(),
                )
            )
            raise UnsupportedConfigAfterUpdateError(
                config_model.pricing_type, config_model.config_type
            )

        elif (
            config_model.config_type == PricingImplementationTypes.fee.value
            and config_model.pricing_type == PricingTypes.peak.value
            and (
                len(self._get_discounts_grids()) > 0
                or len(self._get_volume_grids()) > 0
            )
        ):
            self.logger.warn(
                LogMsg.unsupported_config_grid.format(
                    grid=config_model.pricing_type.upper(),
                    config=config_model.config_type.upper(),
                )
            )
            raise UnsupportedConfigAfterUpdateError(
                config_model.pricing_type, config_model.config_type
            )

        elif (
            config_model.config_type == PricingImplementationTypes.fee.value
            and config_model.pricing_type == PricingTypes.volume.value
            and (
                len(self._get_discounts_grids()) > 0 or len(self._get_peak_grids()) > 0
            )
        ):
            self.logger.warn(
                LogMsg.unsupported_config_grid.format(
                    grid=config_model.pricing_type.upper(),
                    config=config_model.config_type.upper(),
                )
            )
            raise UnsupportedConfigAfterUpdateError(
                config_model.pricing_type, config_model.config_type
            )

    def get_config(self, config_model: BaseConfig) -> ConfigResp:
        if (
            config_model.config_type == PricingImplementationTypes.discount.value
            and config_model.pricing_type == PricingTypes.volume.value
        ):
            grids = self._get_discounts_grids()

        elif (
            config_model.config_type == PricingImplementationTypes.fee.value
            and config_model.pricing_type == PricingTypes.peak.value
        ):
            grids = self._get_peak_grids()

        elif (
            config_model.config_type == PricingImplementationTypes.fee.value
            and config_model.pricing_type == PricingTypes.volume.value
        ):
            grids = self._get_volume_grids()

        return ConfigResp(
            client_id=config_model.client_id,
            valid_from=config_model.valid_from,
            valid_to=config_model.valid_to,
            pricing_type=config_model.pricing_type,
            config_type=config_model.config_type,
            group=config_model.group,
            package_size_option=config_model.package_size_option,
            transport_option=config_model.transport_option,
            frequency=config_model.frequency,
            deleted_at=config_model.deleted_at,
            grids=grids,
        )


class ConfigDeleteController:
    client_id: int
    db: db_dependency
    logger: Logger

    def __init__(self, client_id: int, db: db_dependency, logger: Logger) -> None:
        self.client_id: int = client_id
        self.db: db_dependency = db
        self.logger: Logger = logger

    def _get_all_configs(self) -> list[ConfigTable]:
        return (
            self.db.query(ConfigTable)
            .filter(ConfigTable.client_id == self.client_id)
            .all()
        )

    def _get_last_config(self) -> ConfigTable:
        return (
            self.db.query(ConfigTable)
            .filter(ConfigTable.client_id == self.client_id)
            .filter(ConfigTable.deleted_at.is_(None))
            .order_by(desc(ConfigTable.valid_to))
            .first()
        )

    def _get_config_ids(self, models_to_delete: list[ConfigTable]) -> list[int]:
        return [model.id for model in models_to_delete]

    def _get_client_ids(self, models_to_delete: list[ConfigTable]) -> list[int]:
        return [model.client_id for model in models_to_delete]

    def delete_all(self) -> None:
        models_to_delete = self._get_all_configs()
        if len(models_to_delete) == 0:
            self.logger.info(
                AppVars.no_client_config.value.format(client_id=self.client_id)
            )
            return Response(
                content=AppVars.no_client_config.value.format(client_id=self.client_id),
                status_code=status.HTTP_200_OK,
            )

        for model in models_to_delete:
            model.deleted_at = datetime.now()
            self.db.add(model)

        self.db.commit()
        self.logger.info(
            LogMsg.config_deleted.value.format(
                config_id=self._get_config_ids(),
                client_id=self._get_client_ids(),
            )
        )

    def delete_last(self) -> None:
        model_to_delete = self._get_last_config()

        if model_to_delete is None:
            self.logger.info(
                AppVars.no_client_config.value.format(client_id=self.client_id)
            )
            return Response(
                content=AppVars.no_client_config.value.format(client_id=self.client_id),
                status_code=status.HTTP_200_OK,
            )

        model_to_delete.deleted_at = datetime.now()
        self.db.add(model_to_delete)
        self.db.commit()
        self.logger.info(
            LogMsg.config_deleted.value.format(
                config_id=model_to_delete.id, client_id=model_to_delete.client_id
            )
        )
