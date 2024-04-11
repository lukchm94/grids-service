from pydantic import BaseModel, Field, root_validator

from __app_configs import HttpMethods, Paths, Permissions
from __exceptions import InvalidInputError


class Route(BaseModel):
    method: str
    endpoint: str

    @root_validator(pre=True)
    def validate(cls, values: dict) -> dict:
        method: str = values.get("method")
        endpoint: str = values.get("endpoint")

        if method not in HttpMethods.list():
            raise InvalidInputError(method)

        if not endpoint.startswith(Paths.root.value):
            raise InvalidInputError(endpoint)

        return values


class Permission(BaseModel):
    method: str = Field(default=HttpMethods.get.value)
    permission: str = Field(default=Permissions.read.value)
    endpoint: str = Field(default=Paths.root.value)

    @root_validator(pre=True)
    def validate_permission(cls, values: dict) -> dict:
        method: str = values.get("method")
        permission: str = values.get("permission")
        endpoint: str = values.get("endpoint")

        if method not in HttpMethods.list():
            raise InvalidInputError(method)

        if permission not in Permissions.list():
            raise InvalidInputError(permission)

        if not endpoint.startswith(Paths.root.value):
            raise InvalidInputError(method)

        return values


class PermissionReq(BaseModel):
    method: str = Field(default=HttpMethods.get.value)
    permission: str = Field(default=Permissions.read.value)
    endpoints: list[str] = Field(default=[Paths.root.value])

    @root_validator(pre=True)
    def validate_permission(cls, values: dict) -> dict:
        method: str = values.get("method")
        permission: str = values.get("permission")
        endpoints: str = values.get("endpoints")

        if method not in HttpMethods.list():
            raise InvalidInputError(method)

        if permission not in Permissions.list():
            raise InvalidInputError(permission)

        for endpoint in endpoints:
            # Ideally we would add some validation if the endpoints exists in the app
            # I found sth like this from server.main import app print(app.routes)
            # but possibly there is a nicer way to store the endpoints in a
            # json file or sth like that directly from server/main.py
            if not endpoint.startswith(Paths.root.value):
                raise InvalidInputError(endpoint)

        return values
