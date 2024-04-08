import base64
from logging import Logger
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm

from __app_configs import return_elements
from __exceptions import AuthenticationError, UserNotFoundError
from auth.main import Token
from database.main import db_dependency
from database.models import UsersTable
from models.users import User, UserReq, UserWithToken


class Getter:
    logger: Logger
    db: db_dependency

    def __init__(self, logger: Logger, db: db_dependency) -> None:
        self.logger: Logger = logger
        self.db: db_dependency = db

    def get_all_users(self) -> dict:
        users: list[UsersTable] = self.db.query(UsersTable).all()
        if len(users) == 0:
            raise UserNotFoundError()
        return return_elements([user.to_user() for user in users])

    def get_user(self, username: str, password: str) -> User:
        user: UsersTable = (
            self.db.query(UsersTable).filter(UsersTable.username == username).first()
        )
        if user is None:
            raise UserNotFoundError(username)
        if user.hashed_password != base64.b64encode(password.encode()).decode():
            raise AuthenticationError(username)

        return user.to_user()

    def generate_token(
        self, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
    ) -> UserWithToken:
        user: User = self.get_user(
            username=form_data.username, password=form_data.password
        )
        if user is None:
            raise UserNotFoundError(form_data.username)

        return Token(user).generate_token()


class Setter:
    logger: Logger
    db: db_dependency
    user_req: UserReq

    def __init__(self, logger: Logger, db: db_dependency, user_req: UserReq) -> None:
        self.logger: Logger = logger
        self.db: db_dependency = db
        self.user_req: UserReq = user_req

    def create_user(self) -> None:
        create_user_model: UsersTable = UsersTable(
            email=self.user_req.email,
            username=self.user_req.username,
            first_name=self.user_req.first_name,
            last_name=self.user_req.last_name,
            role=self.user_req.role,
            hashed_password=base64.b64encode(self.user_req.password.encode()).decode(),
            deleted_at=None,
        )
        self.db.add(create_user_model)
        self.db.commit()
