from fastapi import APIRouter, Request, status

from __app_configs import Paths
from auth.check_access import authorize
from auth.main import user_dependency
from database.main import db_dependency
from models.users import UserReq
from services.users.impl import Getter, Setter
from utils.logger import logger

router = APIRouter(prefix=Paths.user.value, tags=[Paths.user_tag.value])


@router.get(Paths.root.value, status_code=status.HTTP_200_OK)
async def get_users(db: db_dependency, user: user_dependency, req: Request) -> dict:
    authorize(user, db, req.method, Paths.user.value + Paths.root.value)
    try:
        return Getter(logger, db).get_all_users()
    except Exception as err:
        logger.error(err)


@router.post(Paths.root.value, status_code=status.HTTP_201_CREATED)
async def create_users(
    db: db_dependency, user_req: UserReq, user: user_dependency, req: Request
) -> None:
    authorize(user, db, req.method, Paths.user.value + Paths.root.value)
    try:
        Setter(logger, db, user_req).create_user()
    except Exception as err:
        logger.error(err)


# TODO add endpoints to change password and update permissions
# @router.put(Paths.root.value)
# async def change_password():
#     pass
