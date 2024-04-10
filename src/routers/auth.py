from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from __app_configs import Paths
from database.main import db_dependency
from models.users import UserWithToken
from services.users.generate_token import generate_token
from utils.logger import logger

router = APIRouter(prefix=Paths.auth.value, tags=[Paths.auth_tag.value])


@router.post(
    Paths.token.value, response_model=UserWithToken, status_code=status.HTTP_200_OK
)
async def get_access_token(
    db: db_dependency, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> None:
    try:
        return generate_token(form_data, logger, db)

    except Exception as err:
        logger.error(err)
