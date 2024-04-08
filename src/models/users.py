from pydantic import BaseModel, Field, root_validator

from __exceptions import PasswordUpdateException
from models.token import Token


class User(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    email: str = Field(min_length=3, include="@")
    password: str = Field(min_length=3, max_length=100)
    role: str = Field(min_length=3, max_length=100)

    # TODO add email validations with re


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
