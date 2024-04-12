import re

from pydantic import BaseModel, Field, root_validator

from __app_configs import Deliminator, Permissions, Roles
from __exceptions import InvalidEmailError, InvalidInputError, PasswordUpdateException
from models.token import Token


class User(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    email: str = Field(min_length=3, include="@")
    password: str = Field(min_length=3, max_length=100)
    role: str = Field(min_length=3, max_length=100, default=Roles.user.value)
    permissions: list[str] = Field(default=Permissions.list())

    @staticmethod
    def _is_valid_email(email: str) -> bool:
        email_regex: re.Pattern = re.compile(
            r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        )
        return bool(
            re.match(
                email_regex,
                email.replace(Deliminator.space.value, Deliminator.none.value),
            )
        )

    @root_validator(pre=True)
    def validate_user(cls, values: dict) -> dict:
        email: str = values.get("email")
        role: str = values.get("role")
        permissions: list[str] = values.get("permissions")

        if not User._is_valid_email(email):
            raise InvalidEmailError(email)

        if role not in Roles.list():
            raise InvalidInputError(role)

        for permission in permissions:
            if permission not in Permissions.list():
                raise InvalidInputError(permission)

        return values


class UserReq(User):
    first_name: str = Field(min_length=3, max_length=100)
    last_name: str = Field(min_length=3, max_length=100)


class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=6)

    @root_validator(pre=True)
    def validate_passwords(cls, values: dict) -> dict:
        password: str = values.get("password")
        new_password: str = values.get("new_password")

        if password == new_password:
            raise PasswordUpdateException()

        return values


class UserWithToken(Token):
    user: User


class CurrentUser(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    role: str = Field(min_length=3, max_length=100)
    permissions: list[str]

    @root_validator(pre=True)
    def validate_user(cls, values: dict) -> dict:
        role: str = values.get("role")
        permissions: str = values.get("permissions")

        if role not in Roles.list():
            raise InvalidInputError(role)
        for permission in permissions:
            if permission not in Permissions.list():
                raise InvalidInputError(permissions)

        return values
