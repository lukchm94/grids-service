from logging import Logger

from fastapi import Response, status
from sqlalchemy import desc

from __app_configs import LogMsg, return_elements
from controllers.account import AccountReqController, AccountRespController
from database.main import db_dependency
from database.models import AccountTable
from models.account import Account, AccountBaseReq


class Getter:
    logger: Logger
    db: db_dependency

    def __init__(self, logger: Logger, db: db_dependency) -> None:
        self.logger: Logger = logger
        self.db: db_dependency = db

    def _missing_acount(self) -> Response:
        return Response(
            content=LogMsg.missing_group.value,
            status_code=status.HTTP_204_NO_CONTENT,
        )

    def all_accounts_by_client_id(self, client_id: int) -> None:
        account_models: list[AccountTable] = (
            self.db.query(AccountTable)
            .filter(AccountTable.client_ids.like(f"%{client_id}%"))
            .filter(AccountTable.deleted_at.is_(None))
            .order_by(desc(AccountTable.valid_to))
            .all()
        )

        return (
            self._missing_acount()
            if len(account_models) == 0
            else AccountRespController(account_models).resp()
        )

    def all_accounts_by_id(self, id: int) -> None:
        account_models: list[AccountTable] = (
            self.db.query(AccountTable)
            .filter(AccountTable.id == id)
            .order_by(desc(AccountTable.valid_to))
            .all()
        )

        if len(account_models) == 0:
            return self._missing_acount()

        accounts: list[Account] = [model.to_account() for model in account_models]
        return return_elements(accounts)

    def last_accounts_by_id(self, id: int) -> None:
        account_model: AccountTable = (
            self.db.query(AccountTable)
            .filter(AccountTable.deleted_at.is_(None))
            .filter(AccountTable.id == id)
            .order_by(desc(AccountTable.valid_to))
            .first()
        )

        return (
            self._missing_acount()
            if account_model is None
            else account_model.to_account()
        )


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

    def create_account(self, return_account: bool = False):
        req_controller = AccountReqController(self.account_req, self.logger)
        if req_controller.check_if_exists(self.db):
            return Response(
                content=LogMsg.client_id_in_account.value,
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        valid_req = req_controller.format()
        account_model = AccountTable(**valid_req.model_dump())
        self.db.add(account_model)
        self.db.commit()
        account = self.db.query(AccountTable).order_by(desc(AccountTable.id)).first()
        self.logger.info(
            LogMsg.account_created.value.format(
                client_id=account.id, client_ids=account_model.client_ids
            )
        )
        if return_account:
            return account.id
