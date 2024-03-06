from __future__ import annotations

from __app_configs import Deliminator
from database.main import db_dependency
from database.models import ConfigTable
from models.configs import BaseConfig, ConfigReq


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

    def check_existing_config(self, db: db_dependency) -> bool:
        # TODO validate if the configuration for a client_id exists
        pass


class ConfigModelController:
    config_model: ConfigTable

    def __init__(self, config_model: ConfigTable) -> ConfigModelController:
        self.config_model = config_model
