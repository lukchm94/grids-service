from pydantic import BaseModel, model_validator

from __app_configs import Paths, Permissions, ValidationEnum

# TODO update the permissions of the remaining endpoints
# Data permission mapped as permission: [list of endpoints]
GET_PERM: dict = {Permissions.read.value: [Paths.user.value + Paths.root.value]}
POST_PERM: dict = {Permissions.write.value: [Paths.user.value + Paths.root.value]}
DEL_PERM: dict = {}
PUT_PERM: dict = {}


class HttpMethods(str, ValidationEnum):
    get = "GET"
    post = "POST"
    delete = "DELETE"
    put = "PUT"


class Route(BaseModel):
    method: str
    endpoint: str

    @model_validator(mode="before")
    def validate(cls, values: dict) -> dict:
        method: str = values.get("method")
        endpoint: str = values.get("endpoint")
        if method not in HttpMethods.list():
            raise ValueError("Invalid HTTP method")
        if not (
            endpoint.startswith(Paths.root.value)
            and endpoint.endswith(Paths.root.value)
        ):
            raise ValueError("Invalid endpoint path")
        return values


class Access:
    route: Route
    user_perm: list[str]

    def __init__(self, user_perm: list[str], endpoint: str, method: str) -> None:
        self.route: Route = Route(method=method, endpoint=endpoint)
        self.user_perm: list[str] = user_perm

    def _get_endpoints(self) -> dict:
        allowed_endpoints: dict = {}

        if self.route.method == HttpMethods.get.value:
            allowed_endpoints.update(GET_PERM)

        elif self.route.method == HttpMethods.post.value:
            allowed_endpoints.update(POST_PERM)

        elif self.route.method == HttpMethods.delete.value:
            allowed_endpoints.update(DEL_PERM)

        elif self.route.method == HttpMethods.put.value:
            allowed_endpoints.update(PUT_PERM)

        return allowed_endpoints

    def check(self) -> bool:
        endpoints: dict = self._get_endpoints()
        for perm in self.user_perm:
            if endpoints.get(perm) is None:
                continue

            return self.route.endpoint in endpoints.get(perm)
        return False
