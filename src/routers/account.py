from datetime import datetime

from fastapi import APIRouter, Path, Query, Request, status

from __app_configs import Paths
from auth.check_access import authorize
from auth.main import user_dependency
from database.main import db_dependency
from models.account import AccountBaseReq
from models.query_req import DatesReq
from services.account.impl import Getter, Setter
from services.account.service import AccountDeleteController
from utils.logger import logger
from utils.query_req import DateReqController

router = APIRouter(prefix=Paths.acct.value, tags=[Paths.account_tag.value])


@router.get(Paths.all_acct_by_client.value + "{id}", status_code=status.HTTP_200_OK)
async def get_all_accounts_by_client_id(
    db: db_dependency, user: user_dependency, req: Request, id: int = Path(gt=0)
):
    authorize(user, req.method, Paths.acct.value + Paths.all_acct_by_client.value)
    try:
        return Getter(logger, db).all_accounts_by_client_id(id)

    except Exception as err:
        logger.error(err)


@router.get(Paths.acct_by_client_date.value + "{id}", status_code=status.HTTP_200_OK)
async def get_accounts_by_client_id_date(
    db: db_dependency,
    user: user_dependency,
    req: Request,
    id: int = Path(gt=0),
    start: datetime = Query(None),
    end: datetime = Query(None),
):
    authorize(user, req.method, Paths.acct.value + Paths.acct_by_client_date.value)
    dates_req: DatesReq = DateReqController(start, end).format()
    try:
        return Getter(logger, db).accounts_by_client_id_date(dates_req, id)

    except Exception as err:
        logger.error(err)


@router.post(Paths.root.value, status_code=status.HTTP_201_CREATED)
async def create_account(
    db: db_dependency, user: user_dependency, account_req: AccountBaseReq, req: Request
):
    authorize(user, req.method, Paths.acct.value + Paths.root.value)
    try:
        Setter(logger, db, account_req).create_account()

    except Exception as err:
        logger.error(err)


@router.put(Paths.delete_account.value + "{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    db: db_dependency, user: user_dependency, req: Request, id: int = Path(gt=0)
):
    authorize(user, req.method, Paths.acct.value + Paths.delete_account.value)
    try:
        AccountDeleteController(id, db, logger).delete()

    except Exception as err:
        logger.error(err)
