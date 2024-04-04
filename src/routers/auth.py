from fastapi import APIRouter, status

from __app_configs import Paths
from controllers.auth_impl import Getter, Setter
from database.main import db_dependency
from models.users import UserReq
from utils.logger import logger

router = APIRouter(prefix=Paths.auth.value, tags=[Paths.auth_tag.value])


@router.get(Paths.root.value, status_code=status.HTTP_200_OK)
async def get_users() -> None:
    return Getter(logger, db_dependency).get_all_users()
    # try:
    #     return Getter(logger, db_dependency).get_all_users()
    # except Exception as err:
    #     logger.error(err)


@router.post(Paths.root.value, status_code=status.HTTP_201_CREATED)
async def create_users(user_req: UserReq) -> None:
    # Setter(logger, db_dependency).create_user(user_req)
    try:
        Setter(logger, db_dependency, user_req).create_user()
    except Exception as err:
        logger.error(err)
