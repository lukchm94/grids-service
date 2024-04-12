from fastapi import APIRouter, Path, Request, status

from __app_configs import Paths
from auth.check_access import authorize
from auth.main import user_dependency
from database.main import db_dependency
from models.users import UserReq, UserVerification
from services.users.impl import Getter, Setter, Update
from utils.logger import logger

router = APIRouter(prefix=Paths.user.value, tags=[Paths.user_tag.value])


@router.get(Paths.root.value + "{username}", status_code=status.HTTP_200_OK)
async def get_users(
    db: db_dependency, user: user_dependency, req: Request, username: str
) -> dict:
    authorize(user, db, req.method, Paths.user.value + Paths.root.value)
    try:
        return Getter(logger, db).get_user_by_username(username)
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


@router.put(Paths.password.value, status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    db: db_dependency,
    user_ver: UserVerification,
    user: user_dependency,
    req: Request,
):
    authorize(user, db, req.method, Paths.user.value + Paths.password.value)
    try:
        Update(logger, db, user).change_password(user_ver)
    except Exception as err:
        logger.error(err)


@router.put(
    Paths.permissions.value + Paths.root.value + "{username}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def change_permissions(
    db: db_dependency,
    permissions: list[str],
    user: user_dependency,
    req: Request,
    username: str = Path,
):
    authorize(user, db, req.method, Paths.permissions.value + Paths.root.value)
    try:
        Update(logger, db, user).change_permissions(permissions, username)
    except Exception as err:
        logger.error(err)
