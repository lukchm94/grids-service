from datetime import datetime
from logging import Logger

from fastapi import APIRouter, Path, Query, status

from __app_configs import Paths
from controllers.config_impl import Getter, Setter
from controllers.query_req import DateReqController
from database.main import db_dependency
from models.configs import BaseConfig, Config
from models.query_req import DatesReq
from utils.logger import get_cloudwatch_logger

logger: Logger = get_cloudwatch_logger()
router = APIRouter(prefix=Paths.configs.value, tags=[Paths.config_tag.value])


@router.get(Paths.config_dates.value + "{client_id}", status_code=status.HTTP_200_OK)
async def get_config_by_client_date(
    db: db_dependency,
    client_id: int = Path(gt=0),
    start: datetime = Query(None),
    end: datetime = Query(None),
):
    dates_req: DatesReq = DateReqController(start, end).format()
    try:
        return Getter(logger, db).config_by_client_id_date(dates_req, client_id)
    except Exception as err:
        logger.error(err)


@router.get(Paths.all_config.value + "{client_id}", status_code=status.HTTP_200_OK)
async def get_configs_by_client_id(db: db_dependency, client_id: int = Path(gt=0)):
    try:
        return Getter(logger, db).all_config_by_client_id(client_id)
    except Exception as err:
        logger.error(err)


@router.post(Paths.ind.value + "{id}", status_code=status.HTTP_201_CREATED)
async def create_ind_config(db: db_dependency, req: Config, id: int = Path(gt=0)):
    try:
        Setter(logger, db).create_ind_config(req, id)
    except Exception as err:
        logger.error(err)


@router.post(Paths.group.value + "{id}", status_code=status.HTTP_201_CREATED)
async def create_group_config(db: db_dependency, req: Config, id: int = Path(gt=0)):
    try:
        Setter(logger, db).create_group_config(req, id)
    except Exception as err:
        logger.error(err)


@router.put(Paths.root.value + "{id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_last_config(db: db_dependency, req: BaseConfig, id: int = Path(gt=0)):
    try:
        Setter(logger, db).update_last_config(req, id)
    except Exception as err:
        logger.error(err)


@router.put(Paths.del_all_config.value + "{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_config(db: db_dependency, id: int = Path(gt=0)):
    try:
        Setter(logger, db).delete_all(id)
    except Exception as err:
        logger.error(err)


@router.put(
    Paths.del_last_config.value + "{id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_last_config(db: db_dependency, id: int = Path(gt=0)):
    try:
        Setter(logger, db).delete_last(id)
    except Exception as err:
        logger.error(err)
