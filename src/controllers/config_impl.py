from datetime import datetime
from logging import Logger

from sqlalchemy import desc

from __app_configs import Defaults, Groups, LogMsg, return_elements
from __exceptions import (
    AccountNotFoundError,
    ConfigGroupError,
    InvalidGroupError,
    MissingGridsError,
)
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
from models.account import Account, AccountBaseReq
from models.configs import BaseConfig, Config, ConfigReq, ConfigResp
from models.query_req import DatesReq


class Getter:
    logger: Logger
    db: db_dependency

    def __init__(self, logger: Logger, db: db_dependency) -> None:
        self.logger: Logger = logger
        self.db: db_dependency = db

    def _get_account(self, client_id: int, dates_req: DatesReq = None) -> Account:
        account_controller = ClientAccountController(
            client_id=client_id, db=self.db, logger=self.logger
        )
        return (
            account_controller.get_account_from_dates(dates_req)
            if dates_req is not None
            else account_controller.get_account()
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
        """
        This function retrieves configuration data based on client ID and dates requested.

        :param dates_req: DatesReq object containing the start and end dates for configuration retrieval
        :type dates_req: DatesReq
        :param client_id: The `client_id` parameter in the `config_by_client_id_date` method is an
        integer value that represents the unique identifier of a client for whom the configuration needs
        to be retrieved based on the specified dates
        :type client_id: int
        :return: The function `config_by_client_id_date` is returning the result of the
        `_get_list_configs` method called with the `config_model` as an argument.
        This return a complete Client Configuration with Grids (ConfigResp object)
        """
        account = self._get_account(client_id, dates_req)
        config_model: ConfigTable = (
            self.db.query(ConfigTable)
            .filter(ConfigTable.account_id == account.account_id)
            .filter(ConfigTable.valid_from <= dates_req.start)
            .filter(ConfigTable.valid_to > dates_req.end)
            .filter(ConfigTable.deleted_at.is_(None))
            .order_by(desc(ConfigTable.valid_to))
            .first()
        )
        if config_model is None:
            self._missing_account(client_id)

        return self._get_list_configs(config_model)

    def all_config_by_client_id(self, client_id: int) -> None:
        """
        This function retrieves all configuration data associated with a specific client ID and returns
        it with additional processing.

        :param client_id: The `client_id` parameter is an integer value that represents the unique
        identifier of a client in the system. This identifier is used to retrieve account information
        and configurations associated with that specific client
        :type client_id: int
        :return: The function `all_config_by_client_id` is returning the elements obtained after
        processing the configurations associated with the provided client ID. It retrieves the account
        information, fetches the configuration models from the database based on the account ID, filters
        out any deleted configurations, and then processes the obtained configuration models to include
        grids. Finally, it returns the elements resulting from this processing using the
        `return_elements` function.
        This return a list of complete Client Configurations with Grids (list[ConfigResp] object)
        """
        account = self._get_account(client_id)
        config_models: list[ConfigTable] = (
            self.db.query(ConfigTable)
            .filter(ConfigTable.account_id == account.account_id)
            .filter(ConfigTable.deleted_at.is_(None))
            .all()
        )
        if len(config_models) == 0:
            self._missing_account(client_id)

        configs_with_grids = self._get_list_configs(config_models)
        return return_elements(configs_with_grids)


class Setter:
    logger: Logger
    db: db_dependency

    def __init__(self, logger: Logger, db: db_dependency) -> None:
        self.logger: Logger = logger
        self.db: db_dependency = db

    def _get_config_ids(self, models_to_delete: list[ConfigTable]) -> list[int]:
        return [model.id for model in models_to_delete]

    def _get_account_ids(self, models_to_delete: list[ConfigTable]) -> list[int]:
        return [model.account_id for model in models_to_delete]

    def _missing_account(self, account_id: int) -> None:
        self.logger.warn(LogMsg.account_not_found.value.format(account_id=account_id))
        raise AccountNotFoundError(account_id=account_id)

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
        """
        The `_expire` function checks for existing configurations associated with an account, expires
        them based on validity dates, and raises an error if the configuration group does not match the
        valid request group.

        :param req_controller: The `req_controller` parameter is an instance of the
        `ConfigReqController` class, which is used to handle configuration requests
        :type req_controller: ConfigReqController
        :param valid_req: `valid_req` is an instance of `ConfigReq` class representing a valid
        configuration request
        :type valid_req: ConfigReq
        :param account_id: The `account_id` parameter is an integer value that represents the unique
        identifier of an account in the system. It is used to identify the account for which the
        expiration of configuration models needs to be checked and processed
        :type account_id: int
        """
        if req_controller.check_if_exists(self.db, account_id):
            models_to_expire: list[ConfigTable] = (
                self.db.query(ConfigTable)
                .filter(ConfigTable.account_id == account_id)
                .order_by(ConfigTable.valid_to)
                .all()
            )
            for model in models_to_expire:
                if model.group != valid_req.group:
                    raise ConfigGroupError(
                        account_id=model.account_id,
                        req_group=valid_req.group,
                        existing_group=model.group,
                    )
                if model.valid_to < valid_req.valid_from:
                    continue
                ConfigModelController(model).expire(valid_req, self.db, self.logger)

    def _check_account(
        self, req: Config, client_id: int, req_controller: ConfigReqController
    ) -> ConfigReq:
        """
        The function `_check_account` retrieves or creates a client account and formats a configuration
        request.

        :param req: The `req` parameter is of type `Config`, which is used to store configuration
        settings or data needed for processing the request. It likely contains information such as API
        keys, endpoints, or other configuration details
        :type req: Config
        :param client_id: The `client_id` parameter in the `_check_account` method is an integer that
        represents the unique identifier of a client. It is used to retrieve the account information
        associated with that client from the database
        :type client_id: int
        :param req_controller: The `req_controller` parameter in the `_check_account` method is an
        instance of the `ConfigReqController` class. It is used to control and format configuration
        requests related to a specific account
        :type req_controller: ConfigReqController
        :return: The method `_check_account` is returning a `ConfigReq` object named `valid_req`.
        """
        account = ClientAccountController(client_id, self.db, self.logger).get_account()

        if account is None:
            account_req = self._create_account_req(client_id)
            account: Account = account_impl.Setter(
                logger=self.logger, db=self.db, account_req=account_req
            ).create_account(return_account=True)
        req_controller: ConfigReqController = ConfigReqController(req)
        valid_req: ConfigReq = req_controller.format(account.account_id)
        self._expire(req_controller, valid_req, account.account_id)

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

    def _upload_grids(self, req: Config, config_id: int, valid_req: ConfigReq) -> None:
        GridReqController(req=req, id=config_id).upload(self.db)
        self.db.commit()
        self.logger.info(
            LogMsg.grids_created.value.format(
                config_id=config_id, account_id=valid_req.account_id
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

    def _get_all_configs(self, account_id: int) -> list[ConfigTable]:
        return (
            self.db.query(ConfigTable)
            .filter(ConfigTable.account_id == account_id)
            .all()
        )

    def _get_last_config(self, account_id: int) -> ConfigTable:
        return (
            self.db.query(ConfigTable)
            .filter(ConfigTable.account_id == account_id)
            .filter(ConfigTable.deleted_at.is_(None))
            .order_by(desc(ConfigTable.valid_to))
            .first()
        )

    def create_ind_config(self, req: Config, client_id: int) -> None:
        """
        The function `create_ind_config` validates and uploads configuration data for an individual
        client, handling missing grids and invalid group errors.

        :param req: Config object containing configuration details
        :type req: Config
        :param client_id: The `client_id` parameter in the `create_ind_config` method is an integer
        value that represents the unique identifier of a client for whom the individual configuration is
        being created. This identifier is used to associate the configuration with the specific client
        in the system
        :type client_id: int
        """
        if len(req.grids) == 0:
            raise MissingGridsError()
        if req.group == Groups.group.value:
            raise InvalidGroupError(group=req.group, req_type=Groups.individual.value)

        req_controller: ConfigReqController = ConfigReqController(req)
        valid_req: ConfigReq = self._check_account(req, client_id, req_controller)
        last_config_id = self._upload_config(valid_req)
        self._upload_grids(req, last_config_id, valid_req)

    def create_group_config(self, req: Config, account_id: int) -> None:
        """
        The function `create_group_config` checks and processes a configuration request for a group,
        handling various validations and uploads.

        :param req: The `req` parameter is of type `Config`, which likely contains configuration
        information for a group. It seems to have attributes like `grids` and `group`. The `account_id`
        parameter is an integer representing the account ID associated with this configuration
        :type req: Config
        :param account_id: The `account_id` parameter in the `create_group_config` method is an integer
        value that represents the unique identifier of the account for which the group configuration is
        being created
        :type account_id: int
        """
        if len(req.grids) == 0:
            raise MissingGridsError()
        if req.group == Groups.individual.value:
            raise InvalidGroupError(group=req.group, req_type=Groups.group.value)

        req_controller: ConfigReqController = ConfigReqController(req)
        valid_req: ConfigReq = req_controller.format(account_id)
        if req_controller.check_if_exists(self.db, account_id):
            self._expire(req_controller, valid_req, account_id)

        last_config = self._upload_config(valid_req)
        self._upload_grids(req, last_config, valid_req)

    def update_last_config(self, req: BaseConfig, account_id: int) -> None:
        """
        This Python function updates the last configuration for a specific account based on a given
        request.

        :param req: BaseConfig - an object representing the configuration request
        :type req: BaseConfig
        :param account_id: The `account_id` parameter is an integer value that represents the unique
        identifier of an account for which the configuration needs to be updated. It is used to identify
        the specific account in the database and retrieve the corresponding configuration data for
        updating
        :type account_id: int
        """
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

    def delete_all(self, account_id: int) -> None:
        """
        This Python function deletes all configurations associated with a specific account ID and logs
        the deletion.

        :param account_id: The `account_id` parameter is an integer that is used to identify a specific
        account for which configurations need to be deleted. It is passed to the `delete_all` method to
        specify which account's configurations should be deleted
        :type account_id: int
        """
        models_to_delete: list[ConfigTable] = self._get_all_configs(account_id)
        if len(models_to_delete) == 0:
            raise AccountNotFoundError()

        for model in models_to_delete:
            model.deleted_at = datetime.now()
            self.db.add(model)

        self.db.commit()
        self.logger.info(
            LogMsg.config_deleted.value.format(
                config_id=self._get_config_ids(models_to_delete),
                account_id=self._get_account_ids(models_to_delete),
            )
        )

    def delete_last(self, account_id: int) -> None:
        """
        This Python function deletes the last configuration entry associated with a specific account ID.

        :param account_id: The `account_id` parameter is an integer value that represents the unique
        identifier of an account. It is used to identify the account for which the last configuration
        entry needs to be deleted in the `delete_last` method
        :type account_id: int
        """
        model_to_delete: ConfigTable = self._get_last_config(account_id)

        if model_to_delete is None:
            raise AccountNotFoundError()

        model_to_delete.deleted_at = datetime.now()
        self.db.add(model_to_delete)
        self.db.commit()
        self.logger.info(
            LogMsg.config_deleted.value.format(
                config_id=model_to_delete.id, account_id=model_to_delete.account_id
            )
        )
