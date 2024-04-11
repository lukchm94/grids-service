from fastapi import APIRouter, Path, status

from __app_configs import Paths, Permissions
from auth.check_access import authorize
from auth.main import user_dependency
from database.main import db_dependency
from models.permissions import PermissionReq
from services.permissions.impl import Getter, Setter
from utils.logger import logger

router = APIRouter(prefix=Paths.permissions.value, tags=[Paths.permissions_tag.value])


@router.get(Paths.root.value + "{perm}", status_code=status.HTTP_200_OK)
async def get_permissions_by_name(
    user: user_dependency, db: db_dependency, perm: str = Path
) -> None:
    try:
        return Getter(logger, db).get_perm_by_name(perm)
    except Exception as err:
        logger.error(err)


@router.post(Paths.root.value, status_code=status.HTTP_201_CREATED)
async def create_permission(
    user: user_dependency, db: db_dependency, perm_req: PermissionReq
) -> None:
    try:
        Setter(logger, db, perm_req).create_perm()
    except Exception as err:
        logger.error(err)


@router.put(Paths.root.value + "{perm}", status_code=status.HTTP_204_NO_CONTENT)
async def update_permission(db: db_dependency, perm: str = Path) -> None:
    pass
