from logging import Logger

from fastapi import APIRouter, Path, status

from __app_configs import Paths
from controllers.account import AccountDeleteController
from controllers.account_impl import Getter, Setter
from database.main import db_dependency
from models.account import AccountBaseReq
from utils.logger import get_cloudwatch_logger

logger: Logger = get_cloudwatch_logger()
router = APIRouter(prefix=Paths.accounts.value, tags=[Paths.account_tag.value])


@router.get(Paths.all_acct_by_client.value + "{id}", status_code=status.HTTP_200_OK)
async def get_all_accounts_by_client_id(db: db_dependency, id: int = Path(gt=0)):
    try:
        Getter(logger, db).all_accounts_by_client_id(id)

    except Exception as err:
        logger.error(err)


@router.get(Paths.all_accounts.value + "{id}", status_code=status.HTTP_200_OK)
async def get_all_accounts_by_id(db: db_dependency, id: int = Path(gt=0)):
    try:
        Getter(logger, db).all_accounts_by_id(id)

    except Exception as err:
        logger.error(err)


@router.get(Paths.last_account.value + "{id}", status_code=status.HTTP_200_OK)
async def get_last_accounts_by_id(db: db_dependency, id: int = Path(gt=0)):
    try:
        Getter(logger, db).last_accounts_by_id(id)

    except Exception as err:
        logger.error(err)


@router.post(Paths.root.value, status_code=status.HTTP_201_CREATED)
async def create_account(db: db_dependency, account_req: AccountBaseReq):
    try:
        Setter(logger, db, account_req).create_account()

    except Exception as err:
        logger.error(err)


@router.put(Paths.delete_account.value + "{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(db: db_dependency, id: int = Path(gt=0)):
    try:
        AccountDeleteController(id, db, logger).delete()

    except Exception as err:
        logger.error(err)
