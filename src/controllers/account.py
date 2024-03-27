from datetime import datetime, timedelta
from logging import Logger
from typing import Union

from sqlalchemy import desc

from __app_configs import AppVars, LogMsg
from __exceptions import AccountNotFoundError, MultipleAccountsError
from database.main import db_dependency
from database.models import AccountSequenceTable, AccountTable
from models.account import Account, AccountBaseReq, AccountResp
from models.query_req import DatesReq


def _account_ids(accounts: list[AccountTable]) -> list[int]:
    return list(set([account.account_id for account in accounts]))


def _client_ids(accounts: list[AccountTable]) -> list[int]:
    return list(set([account.client_id for account in accounts]))


class AccountReqController:
    req: AccountBaseReq
    logger: Logger
    db: db_dependency

    def __init__(self, req: AccountBaseReq, logger: Logger, db: db_dependency) -> None:
        self.req = req
        self.logger = logger
        self.db = db

    def _get_unique_client_ids(self) -> str:
        return list(set([client_id for client_id in self.req.client_ids]))

    def _add_account_id(self) -> int:
        account_seq_model = AccountSequenceTable()
        self.db.add(account_seq_model)
        self.db.commit()
        account_seq = (
            self.db.query(AccountSequenceTable)
            .filter(AccountSequenceTable.id)
            .order_by(desc(AccountSequenceTable.id))
            .first()
        )
        self.logger.info(
            LogMsg.acct_seq_created.value.format(account_id=account_seq.id)
        )
        return account_seq.id

    def format(self) -> list[Account]:
        account_id: int = self._add_account_id()
        formatted_requests: list[Account] = []
        for id in self._get_unique_client_ids():
            formatted_requests.append(
                Account(
                    account_id=account_id,
                    client_id=id,
                    client_group_name=self.req.client_group_name,
                    valid_from=self.req.valid_from,
                    valid_to=self.req.valid_to,
                    deleted_at=None,
                )
            )
        return formatted_requests

    def check_if_exists(self) -> Union[Account, None]:
        for client_id in self.req.client_ids:
            account = (
                self.db.query(AccountTable)
                .filter(AccountTable.client_id == client_id)
                .filter(AccountTable.deleted_at.is_(None))
                .order_by(AccountTable.valid_to)
                .first()
            )
            if account is not None:
                self.logger.warn(
                    LogMsg.client_id_exists_in_account.value.format(
                        client_id=client_id, account_ids=account.account_id
                    )
                )
                return account.to_account()


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
            .filter(AccountTable.account_id == self.account_id)
            .filter(AccountTable.deleted_at.is_(None))
            .all()
        )

        if len(accounts) == 0:
            raise AccountNotFoundError()

        for model in accounts:
            model.deleted_at = datetime.now()
            model.valid_to = datetime.now()
            if model.valid_to <= model.valid_from:
                model.valid_from = datetime.now() - timedelta(seconds=1)
            self.db.add(model)

        self.db.commit()
        self.logger.info(
            LogMsg.account_deleted.value.format(
                account_id=_account_ids(accounts),
                client_ids=_client_ids(accounts),
            )
        )


class AccountRespController:
    accounts_table: list[AccountTable]
    accounts: list[Account]

    def __init__(self, accounts: list[AccountTable]) -> None:
        self.accounts_table: list[AccountTable] = accounts
        self.accounts: list[Account] = self._to_account()

    def _to_account(self) -> list[Account]:
        return [account.to_account() for account in self.accounts_table]

    def _get_client_ids(self) -> list[int]:
        return [account.client_id for account in self.accounts]

    def format(self) -> AccountResp:
        if len(set(account.account_id for account in self.accounts)) > 1:
            raise MultipleAccountsError(
                account_ids=set(account.account_id for account in self.accounts)
            )

        return AccountResp(
            account_id=self.accounts[0].account_id,
            client_ids=self._get_client_ids(),
            client_group_name=self.accounts[0].client_group_name,
            valid_from=self.accounts[0].valid_from,
            valid_to=self.accounts[0].valid_to,
            deleted_at=self.accounts[0].deleted_at,
        )

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

    def get_account_from_dates(self, dates_req: DatesReq) -> Union[Account, None]:
        account = self.get_account()
        if account is None:
            raise AccountNotFoundError()

        account: AccountTable = (
            self.db.query(AccountTable)
            .filter(AccountTable.deleted_at.is_(None))
            .filter(AccountTable.account_id == account.account_id)
            .filter(AccountTable.valid_from <= dates_req.start)
            .filter(
                (AccountTable.valid_to > dates_req.end)
                | (AccountTable.valid_to.is_(None))
            )
            .order_by(desc(AccountTable.valid_to))
            .first()
        )
        return account.to_account() if account is not None else None

    def get_account(self) -> Union[Account, None]:
        account = (
            self.db.query(AccountTable)
            .filter(AccountTable.client_id == self.client_id)
            .filter(AccountTable.deleted_at.is_(None))
            .order_by(desc(AccountTable.valid_to))
            .first()
        )
        return account if account is not None else None
