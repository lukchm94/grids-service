from __app_configs import HttpMethods, Paths, Permissions
from database.main import db_dependency
from database.models import PermissionTable
from models.permissions import Route

# TODO update the permissions of the remaining endpoints
# Data permission mapped as permission: [list of endpoints]
GET_PERM: dict = {Permissions.read.value: [Paths.user.value + Paths.root.value]}
POST_PERM: dict = {Permissions.write.value: [Paths.user.value + Paths.root.value]}
DEL_PERM: dict = {}
PUT_PERM: dict = {}


class Access:
    route: Route
    user_perm: list[str]
    db: db_dependency

    def __init__(
        self, db: db_dependency, user_perm: list[str], endpoint: str, method: str
    ) -> None:
        self.db: db_dependency = db
        self.user_perm: list[str] = user_perm
        self.route: Route = Route(method=method, endpoint=endpoint)

    def _allowed_endpoints(self) -> None:
        perms = (
            self.db.query(PermissionTable)
            .filter(PermissionTable.method == self.route.method)
            .filter(PermissionTable.permission.in_(self.user_perm))
        )
        # TODO pick up here

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
