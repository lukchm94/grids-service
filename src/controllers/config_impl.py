from logging import Logger

from sqlalchemy import desc

from __app_configs import Defaults, Groups, LogMsg
from __exceptions import AccountNotFoundError, InvalidGroupError, MissingGridsError
from controllers import account_impl
from controllers.account import ClientAccountController
from controllers.configs import (
    ConfigModelController,
    ConfigReqController,
    ConfigRespController,
)
from controllers.grids import GridReqController
from database.main import db_dependency
from database.models import ConfigTable
from models.account import AccountBaseReq
from models.configs import BaseConfig, Config, ConfigReq, ConfigResp
from models.query_req import DatesReq


class Getter:
    logger: Logger
    db: db_dependency

    def __init__(self, logger: Logger, db: db_dependency) -> None:
        self.logger: Logger = logger
        self.db: db_dependency = db

    def _get_account_id(self, client_id: int, dates_req: DatesReq = None) -> int:
        account_controller = ClientAccountController(
            client_id=client_id, db=self.db, logger=self.logger
        )
        return (
            account_controller.get_account_id_from_dates(dates_req)
            if dates_req is not None
            else account_controller.get_account_id()
        )

    def _missing_account(self, account_id: int) -> None:
        self.logger.info(LogMsg.account_not_found.value.format(account_id=account_id))
        raise AccountNotFoundError(account_id=account_id)

    def _get_config_resp(self, config_model: ConfigTable) -> ConfigResp:
        return ConfigRespController(config_model.id, self.db, self.logger).get_config(
            config_model.to_config()
        )

    def _get_list_configs(self, config_models: list[ConfigTable]) -> list[Config]:
        return [self._get_config_resp(model) for model in config_models]

    def config_by_client_id_date(self, dates_req: DatesReq, client_id: int) -> None:
        account_id = self._get_account_id(client_id, dates_req)
        config_model: ConfigTable = (
            self.db.query(ConfigTable)
            .filter(ConfigTable.account_id == account_id)
            .filter(ConfigTable.valid_from <= dates_req.start)
            .filter(ConfigTable.valid_to > dates_req.end)
            .filter(ConfigTable.deleted_at.is_(None))
            .order_by(desc(ConfigTable.valid_to))
            .first()
        )
        return (
            self._get_config_resp(config_model)
            if config_model is not None
            else self._missing_account(client_id)
        )

    def all_config_by_client_id(self, client_id: int) -> None:
        account_id = self._get_account_id(client_id)
        config_models: list[ConfigTable] = (
            self.db.query(ConfigTable)
            .filter(ConfigTable.account_id == account_id)
            .filter(ConfigTable.deleted_at.is_(None))
            .all()
        )

        return (
            self._missing_account(client_id)
            if len(config_models) == 0
            else self._get_list_configs(config_models)
        )


class Setter:
    logger: Logger
    db: db_dependency

    def __init__(self, logger: Logger, db: db_dependency) -> None:
        self.logger: Logger = logger
        self.db: db_dependency = db

    def _missing_account(self, account_id: int) -> None:
        self.logger.warn(LogMsg.account_not_found.value.format(account_id=account_id))
        raise AccountNotFoundError(account_id=account_id)

    def _missing_grids(self) -> None:
        self.logger.warn(LogMsg.missing_grids.value)
        raise MissingGridsError()

    def _create_account_req(self, client_id: int) -> AccountBaseReq:
        return AccountBaseReq(
            client_ids=[client_id],
            client_group_name=Defaults.ind_account_name.value.format(
                client_id=client_id
            ),
        )

    def _expire(
        self, req_controller: ConfigReqController, valid_req: ConfigReq, account_id: int
    ) -> None:
        if req_controller.check_if_exists(self.db, account_id):
            models_to_expire = (
                self.db.query(ConfigTable)
                .filter(ConfigTable.account_id == account_id)
                .order_by(ConfigTable.valid_to)
                .all()
            )
            for model in models_to_expire:
                if model.valid_to < valid_req.valid_from:
                    continue
                ConfigModelController(model).expire(valid_req, self.db, self.logger)

    def _check_account(
        self, req: Config, client_id: int, req_controller: ConfigReqController
    ) -> ConfigReq:
        account_id = ClientAccountController(
            client_id, self.db, self.logger
        ).check_if_exists()

        if account_id is None:
            account_req = self._create_account_req(client_id)
            account_id: int = account_impl.Setter(
                logger=self.logger, db=self.db, account_req=account_req
            ).create_account(return_account=True)
        req_controller: ConfigReqController = ConfigReqController(req)
        valid_req: ConfigReq = req_controller.format(account_id)
        self._expire(req_controller, valid_req, account_id)

        return valid_req

    def _upload_config(self, valid_req: ConfigReq) -> int:
        config_model = ConfigTable(**valid_req.model_dump())
        self.db.add(config_model)
        self.db.commit()
        self.logger.info(
            LogMsg.config_created.value.format(
                config_id=config_model.id, account_id=config_model.account_id
            )
        )
        last_config = self.db.query(ConfigTable).order_by(desc(ConfigTable.id)).first()
        return last_config.id

    def _upload_grids(
        self, req: Config, last_config: int, valid_req: ConfigReq
    ) -> None:
        GridReqController(req=req, id=last_config).upload(self.db)
        self.db.commit()
        self.logger.info(
            LogMsg.grids_created.value.format(
                config_id=last_config, account_id=valid_req.account_id
            )
        )

    def _update_config(self, updated_model: ConfigTable) -> None:
        self.db.add(updated_model)
        self.db.commit()
        self.logger.info(
            LogMsg.config_updated.value.format(
                config_id=updated_model.id, account_id=updated_model.account_id
            )
        )

    # TODO check the logic for creating IND and Group Accounts
    def create_ind_config(self, req: Config, client_id: int) -> None:
        if len(req.grids) == 0:
            self._missing_grids()
        if req.group == Groups.group.value:
            raise InvalidGroupError(group=req.group, req_type=Groups.individual.value)

        req_controller: ConfigReqController = ConfigReqController(req)
        valid_req: ConfigReq = self._check_account(req, client_id, req_controller)
        last_config = self._upload_config(valid_req)
        self._upload_grids(req, last_config, valid_req)

    def create_group_config(self, req: Config, account_id: int) -> None:
        if len(req.grids) == 0:
            self._missing_grids()
        if req.group == Groups.individual.value:
            raise InvalidGroupError(group=req.group, req_type=Groups.group.value)

        req_controller: ConfigReqController = ConfigReqController(req)
        valid_req: ConfigReq = req_controller.format(account_id)
        if req_controller.check_if_exists(self.db, account_id):
            self._expire(req_controller, valid_req, account_id)

        last_config = self._upload_config(valid_req)
        self._upload_grids(req, last_config, valid_req)

    def update_last_config(self, req: BaseConfig, account_id: int) -> None:
        req_controller: ConfigReqController = ConfigReqController(req)
        if not req_controller.check_if_exists(self.db, account_id):
            self._missing_account(account_id)

        valid_config_req = req_controller.format(account_id)
        model_to_update = (
            self.db.query(ConfigTable)
            .filter(ConfigTable.account_id == account_id)
            .filter(ConfigTable.deleted_at.is_(None))
            .order_by(desc(ConfigTable.valid_to))
            .first()
        )

        updated_model = ConfigModelController(model_to_update).update(valid_config_req)
        config_resp_cont = ConfigRespController(updated_model.id, self.db, self.logger)
        config_resp_cont.check_grids(updated_model)

        self._update_config(updated_model)
