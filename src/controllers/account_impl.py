from logging import Logger

from sqlalchemy import desc

from __app_configs import LogMsg
from __exceptions import AccountNotFoundError, ClientIdMappedToAccountError
from controllers.account import (
    AccountReqController,
    AccountRespController,
    ClientAccountController,
)
from database.main import db_dependency
from database.models import AccountTable
from models.account import Account, AccountBaseReq, AccountResp


class Getter:
    logger: Logger
    db: db_dependency

    def __init__(self, logger: Logger, db: db_dependency) -> None:
        self.logger: Logger = logger
        self.db: db_dependency = db

    def all_accounts_by_client_id(self, client_id: int) -> AccountResp:
        account_id = ClientAccountController(
            client_id, self.db, self.logger
        ).get_account_id()

        if account_id is None:
            self.logger.warn(LogMsg.no_account.value.format(client_id=client_id))
            raise AccountNotFoundError()

        account_models: list[AccountTable] = (
            self.db.query(AccountTable)
            .filter(AccountTable.account_id == account_id)
            .filter(AccountTable.deleted_at.is_(None))
            .order_by(desc(AccountTable.valid_to))
            .all()
        )

        if len(account_models) == 0:
            self.logger.warn(LogMsg.no_account.value.format(client_id=client_id))
            raise AccountNotFoundError()

        return AccountRespController(account_models).format()

    def all_accounts_by_id(self, id: int) -> AccountResp:
        account_models: list[AccountTable] = (
            self.db.query(AccountTable)
            .filter(AccountTable.account_id == id)
            .order_by(desc(AccountTable.valid_to))
            .all()
        )

        if len(account_models) == 0:
            raise AccountNotFoundError()

        return AccountRespController(account_models).format()


class Setter:
    logger: Logger
    db: db_dependency
    account_req: AccountBaseReq

    def __init__(
        self, logger: Logger, db: db_dependency, account_req: AccountBaseReq
    ) -> None:
        self.logger: Logger = logger
        self.db: db_dependency = db
        self.account_req: AccountBaseReq = account_req

    def _get_account_id_from_req(self, requests: list[Account]) -> set:
        return set([id.account_id for id in requests])

    def _get_client_ids_from_req(self, requests: list[Account]) -> list[int]:
        return [id.client_id for id in requests]

    def create_account(self, return_account: bool = False):
        req_controller = AccountReqController(self.account_req, self.logger, self.db)
        account = req_controller.check_if_exists()
        if account is not None:
            raise ClientIdMappedToAccountError(
                client_id=account.client_id, account_ids=account.account_id
            )

        valid_requests = req_controller.format()
        for req in valid_requests:
            account_model = AccountTable(**req.model_dump())
            self.db.add(account_model)
        self.db.commit()

        self.logger.info(
            LogMsg.account_created.value.format(
                account_id=self._get_account_id_from_req(valid_requests),
                client_ids=self._get_client_ids_from_req(valid_requests),
            )
        )
        if return_account:
            return valid_requests[0]
