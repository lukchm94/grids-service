from __exceptions import MissingEndpointPermError
from database.main import db_dependency
from database.models import Permission, PermissionTable
from models.permissions import Route


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

    def _required_perm(self) -> list[str]:
        perms = (
            self.db.query(PermissionTable)
            .filter(PermissionTable.method == self.route.method)
            .filter(PermissionTable.endpoint == self.route.endpoint)
        ).all()
        if len(perms) == 0:
            raise MissingEndpointPermError(
                endpoint=self.route.endpoint, method=self.route.method
            )

        return [perm.to_permission().permission for perm in perms]

    def _perm_endpoint(self, perm: str, perms: list[Permission]) -> list[str]:
        return list(set([p.endpoint for p in perms if p.permission == perm]))

    def _allowed_endpoints(self) -> list[Permission]:
        perms = (
            self.db.query(PermissionTable)
            .filter(PermissionTable.method == self.route.method)
            .filter(PermissionTable.permission.in_(self.user_perm))
        ).all()
        if len(perms) == 0:
            raise MissingEndpointPermError(
                endpoint=self.user_perm, method=self.route.method
            )

        return [perm.to_permission() for perm in perms]

    def _get_endpoints(self) -> dict:
        perms: list[Permission] = self._required_perm()
        allowed_endpoints: dict = {}
        for perm in self.user_perm:
            allowed_endpoints.update({perm: self._perm_endpoint(perm, perms)})
        return allowed_endpoints

    def check(self) -> bool:
        required_perms: list[str] = self._required_perm()
        for perm in self.user_perm:
            if perm in required_perms:
                return True
        return False
