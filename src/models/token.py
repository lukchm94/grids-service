from pydantic import BaseModel, Field, root_validator

from __app_configs import TokenTypes
from __exceptions import InvalidTokenType


class Token(BaseModel):
    access_token: str
    token_type: str = Field(default=TokenTypes.bearer.value)

    @root_validator(pre=True)
    def validate_passwords(cls, values: dict) -> dict:
        token_type: str = values.get("token_type")

        if token_type not in TokenTypes.list():
            raise InvalidTokenType(token_type, TokenTypes.to_string())

        return values
