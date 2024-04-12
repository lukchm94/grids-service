from fastapi import APIRouter, Path, Request, status

from __app_configs import Paths
from auth.check_access import authorize
from auth.main import user_dependency
from database.main import db_dependency
from models.permissions import PermissionReq
from services.permissions.impl import Delete, Getter, Setter
from utils.logger import logger

router = APIRouter(prefix=Paths.permissions.value, tags=[Paths.permissions_tag.value])


@router.get(Paths.root.value + "{perm}", status_code=status.HTTP_200_OK)
async def get_permissions_by_name(
    user: user_dependency, db: db_dependency, req: Request, perm: str = Path
) -> None:
    authorize(user, db, req.method, Paths.permissions.value + Paths.root.value)
    try:
        return Getter(logger, db).get_perm_by_name(perm)
    except Exception as err:
        logger.error(err)


@router.post(Paths.root.value, status_code=status.HTTP_201_CREATED)
async def create_permission(
    user: user_dependency, db: db_dependency, perm_req: PermissionReq, req: Request
) -> None:
    authorize(user, db, req.method, Paths.permissions.value + Paths.root.value)
    try:
        Setter(logger, db, perm_req).create_perm()
    except Exception as err:
        logger.error(err)


@router.delete(Paths.root.value + "{perm}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_permission(
    user: user_dependency,
    db: db_dependency,
    req: Request,
    endpoint: str,
    method: str,
    perm: str = Path,
) -> None:
    authorize(user, db, req.method, Paths.permissions.value + Paths.root.value)
    Delete(logger, db).single_access(method, endpoint, perm)
