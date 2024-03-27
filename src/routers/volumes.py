from datetime import datetime

from fastapi import APIRouter, Path, Query, status

from __app_configs import Paths
from controllers.query_req import DateReqController
from controllers.volumes_impl import Getter
from database.main import db_dependency
from models.query_req import DatesReq
from utils.logger import logger

router = APIRouter(prefix=Paths.volumes.value, tags=[Paths.volumes_tag.value])


@router.get(Paths.dates.value + "{id}", status_code=status.HTTP_200_OK)
async def get_volume_from_dates(
    db: db_dependency,
    id: int = Path(gt=0),
    start: datetime = Query(None),
    end: datetime = Query(None),
):
    dates_req: DatesReq = DateReqController(start, end).format()
    try:
        return Getter(logger, db).volumes_from_dates(id, dates_req)
    except Exception as err:
        logger.error(err)
