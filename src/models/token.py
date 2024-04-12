from pydantic import BaseModel, Field, root_validator

from __app_configs import TokenTypes
from __exceptions import AuthenticationError, InvalidTokenType


class Token(BaseModel):
    access_token: str
    token_type: str = Field(default=TokenTypes.bearer.value)

    @root_validator(pre=True)
    def validate_token(cls, values: dict) -> dict:
        try:
            token_type: str = values.get("token_type")
        except Exception:
            raise AuthenticationError()

        if token_type not in TokenTypes.list():
            raise InvalidTokenType(token_type, TokenTypes.to_string())

        return values
