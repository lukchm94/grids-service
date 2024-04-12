from logging import Logger
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm

from __exceptions import UserNotFoundError
from auth.main import Token
from database.main import db_dependency
from models.users import User, UserWithToken
from services.users.impl import Getter


def generate_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    logger: Logger,
    db: db_dependency,
) -> UserWithToken:
    user: User = Getter(logger, db).get_user(
        username=form_data.username, password=form_data.password
    )
    if user is None:
        raise UserNotFoundError(form_data.username)
    return Token(user).generate_token()
