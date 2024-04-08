from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from __app_configs import Paths
from controllers.auth_impl import Getter, Setter
from database.main import db_dependency
from models.users import UserReq, UserWithToken
from utils.logger import logger

router = APIRouter(prefix=Paths.auth.value, tags=[Paths.auth_tag.value])


@router.get(Paths.root.value, status_code=status.HTTP_200_OK)
async def get_users(db: db_dependency) -> None:
    try:
        return Getter(logger, db).get_all_users()
    except Exception as err:
        logger.error(err)


@router.post(Paths.root.value, status_code=status.HTTP_201_CREATED)
async def create_users(db: db_dependency, user_req: UserReq) -> None:
    try:
        Setter(logger, db, user_req).create_user()
    except Exception as err:
        logger.error(err)


@router.post(
    Paths.token.value, response_model=UserWithToken, status_code=status.HTTP_200_OK
)
async def get_access_token(
    db: db_dependency, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> None:
    try:
        return Getter(logger, db).generate_token(form_data)

    except Exception as err:
        logger.error(err)
