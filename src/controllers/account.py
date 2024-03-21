from datetime import datetime
from logging import Logger

from fastapi import Response, status
from sqlalchemy import desc

from __app_configs import AppVars, Deliminator, LogMsg
from database.main import db_dependency
from database.models import AccountTable
from models.account import Account, AccountBaseReq, AccountReq
from models.query_req import DatesReq


def _account_ids(accounts: list[AccountTable]) -> list[int]:
    return [account.id for account in accounts]


def _client_ids(accounts: list[AccountTable]) -> list[int]:
    return list(set([account.client_ids for account in accounts]))


class AccountReqController:
    req: AccountBaseReq
    logger: Logger

    def __init__(self, req: AccountBaseReq, logger: Logger) -> None:
        self.req = req
        self.logger = logger

    def format(self) -> AccountReq:
        return AccountReq(
            client_ids=Deliminator.comma.value.join(
                [str(client_id) for client_id in self.req.client_ids]
            ),
            client_group_name=self.req.client_group_name,
            valid_from=self.req.valid_from,
            valid_to=self.req.valid_to,
            deleted_at=None,
        )

    def check_if_exists(self, db: db_dependency) -> bool:
        for client_id in self.req.client_ids:
            accounts = (
                db.query(AccountTable)
                .filter(AccountTable.client_ids.like(f"%{client_id}%"))
                .filter(AccountTable.deleted_at.is_(None))
                .order_by(AccountTable.valid_to)
                .all()
            )

        if len(accounts) == 0:
            self.logger.warn(
                LogMsg.client_id_exists_in_account.value.format(
                    client_id=client_id, account_ids=_account_ids(accounts)
                )
            )
            return False
        return True


class AccountDeleteController:
    account_id: int
    db: db_dependency
    logger: Logger

    def __init__(self, account_id: int, db: db_dependency, logger: Logger) -> None:
        self.account_id = account_id
        self.db = db
        self.logger = logger

    def delete(self) -> None:
        accounts: list[AccountTable] = (
            self.db.query(AccountTable)
            .filter(AccountTable.id == self.account_id)
            .filter(AccountTable.deleted_at.is_(None))
            .all()
        )

        for model in accounts:
            model.deleted_at = datetime.now()
            self.db.add(model)

        self.db.commit()
        self.logger.info(
            LogMsg.account_deleted.value.format(
                account_id=_account_ids(accounts),
                client_ids=_client_ids(accounts),
            )
        )


class AccountRespController:
    accounts: list[AccountTable]

    def __init__(self, accounts: list[AccountTable]) -> None:
        self.accounts: list[AccountTable] = accounts

    def _to_account(self) -> list[Account]:
        return [account.to_account() for account in self.accounts]

    def resp(self) -> dict:
        return {
            AppVars.elements.value: len(self._to_account()),
            AppVars.group_ids.value: _account_ids(self.accounts),
            AppVars.data.value: self._to_account(),
        }


class ClientAccountController:
    client_id: int
    db: db_dependency
    logger: Logger

    def __init__(self, client_id: int, db: db_dependency, logger: Logger) -> None:
        self.client_id: int = client_id
        self.db: db_dependency = db
        self.logger: Logger = logger

    def _missing_account(self) -> Response:
        return Response(
            content=LogMsg.account_not_found.value.format(account_id=self.client_id),
            status_code=status.HTTP_204_NO_CONTENT,
        )

    def get_account_id(self) -> int:
        account: AccountTable = (
            self.db.query(AccountTable)
            .filter(AccountTable.deleted_at.is_(None))
            .filter(AccountTable.client_ids.like(f"%{self.client_id}%"))
            .order_by(desc(AccountTable.valid_to))
            .first()
        )
        return account.id if account is not None else self._missing_account()

    def check_if_exists(self) -> bool:
        accounts: list[AccountTable] = (
            self.db.query(AccountTable)
            .filter(AccountTable.deleted_at.is_(None))
            .filter(AccountTable.client_ids.like(f"%{self.client_id}%"))
            .order_by(desc(AccountTable.valid_to))
            .all()
        )
        for account in accounts:
            print(account.to_account())
        if len(accounts) == 0:
            self.logger.warn(
                LogMsg.client_id_exists_in_account.value.format(
                    client_id=self.client_id, account_ids=_account_ids(accounts)
                )
            )
            return False
        return True

    def get_account_id_from_dates(self, dates_req: DatesReq) -> int:
        account: AccountTable = (
            self.db.query(AccountTable)
            .filter(AccountTable.deleted_at.is_(None))
            .filter(AccountTable.client_ids.like(f"%{self.client_id}%"))
            .filter(AccountTable.valid_from <= dates_req.start)
            .filter(
                (AccountTable.valid_to > dates_req.end)
                | (AccountTable.valid_to.is_(None))
            )
            .order_by(desc(AccountTable.valid_to))
            .first()
        )
        return account.id if account is not None else self._missing_account()
