from logging import Logger

from __app_configs import LogMsg, return_elements
from database.main import db_dependency
from database.models import PermissionTable
from models.permissions import Permission, PermissionReq


class Getter:
    logger: Logger
    db: db_dependency

    def __init__(self, logger: Logger, db: db_dependency) -> None:
        self.logger: Logger = logger
        self.db: db_dependency = db

    def _to_permissions(self, models: list[PermissionTable]) -> list[Permission]:
        return [model.to_permission() for model in models]

    def get_perm_by_name(self, perm: str) -> Permission:
        models = (
            self.db.query(PermissionTable)
            .filter(PermissionTable.permission == perm)
            .all()
        )

        return return_elements(self._to_permissions(models))


class Setter:
    logger: Logger
    db: db_dependency
    perm_req: PermissionReq

    def __init__(
        self, logger: Logger, db: db_dependency, perm_req: PermissionReq
    ) -> None:
        self.logger: Logger = logger
        self.db: db_dependency = db
        self.perm_req: PermissionReq = perm_req

    def _upload_perm(self) -> None:
        for endpoint in self.perm_req.endpoints:
            model = PermissionTable(
                method=self.perm_req.method,
                permission=self.perm_req.permission,
                endpoint=endpoint,
            )
            self.db.add(model)

    def create_perm(self) -> None:
        print(self)
        self._upload_perm()
        self.db.commit()
        self.logger.info(
            LogMsg.created_perm.value.format(
                perm=self.perm_req.permission, endpoints=self.perm_req.endpoints
            )
        )
