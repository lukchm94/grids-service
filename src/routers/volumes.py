from datetime import datetime

from fastapi import APIRouter, Path, Query, Request, status

from __app_configs import Paths
from auth.check_access import authorize
from auth.main import user_dependency
from database.main import db_dependency
from models.query_req import DatesReq
from services.volumes.impl import Getter
from utils.logger import logger
from utils.query_req import DateReqController

router = APIRouter(prefix=Paths.volumes.value, tags=[Paths.volumes_tag.value])


@router.get(Paths.dates.value + "{id}", status_code=status.HTTP_200_OK)
async def get_daily_volume_from_dates(
    db: db_dependency,
    user: user_dependency,
    req: Request,
    id: int = Path(gt=0),
    start: datetime = Query(None),
    end: datetime = Query(None),
):
    authorize(user, req.method, Paths.volumes.value + Paths.dates.value)
    dates_req: DatesReq = DateReqController(start, end).format()
    try:
        return Getter(logger, db).volumes_from_dates(id, dates_req)
    except Exception as err:
        logger.error(err)


@router.get(Paths.agg_dates.value + "{id}", status_code=status.HTTP_200_OK)
async def get_agg_volume_from_dates(
    db: db_dependency,
    user: user_dependency,
    req: Request,
    id: int = Path(gt=0),
    start: datetime = Query(None),
    end: datetime = Query(None),
):
    authorize(user, req.method, Paths.volumes.value + Paths.agg_dates.value)
    dates_req: DatesReq = DateReqController(start, end).format()
    try:
        return Getter(logger, db).volumes_from_dates(id, dates_req)
    except Exception as err:
        logger.error(err)
