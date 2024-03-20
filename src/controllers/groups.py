from datetime import datetime
from logging import Logger

from __app_configs import AppVars, Deliminator, LogMsg
from database.main import db_dependency
from database.models import ClientGroupsTable
from models.groups import ClientGroup, ClientGroupReq


def _group_ids(client_groups: list[ClientGroupsTable]) -> list[int]:
    return [group.id for group in client_groups]


def _client_ids(client_groups: list[ClientGroupsTable]) -> list[int]:
    return list(set([group.client_ids for group in client_groups]))


class GroupReqController:
    client_group_req: ClientGroup
    logger: Logger

    def __init__(self, client_group_req: ClientGroup, logger: Logger) -> None:
        self.client_group_req = client_group_req
        self.logger = logger

    def format(self) -> ClientGroupReq:
        return ClientGroupReq(
            client_ids=Deliminator.comma.value.join(
                [str(client_id) for client_id in self.client_group_req.client_ids]
            ),
            client_group_name=self.client_group_req.client_group_name,
            valid_from=self.client_group_req.valid_from,
            valid_to=self.client_group_req.valid_to,
            deleted_at=None,
        )

    def check_if_exists(self, db: db_dependency) -> bool:
        for client_id in self.client_group_req.client_ids:
            client_groups = (
                db.query(ClientGroupsTable)
                .filter(ClientGroupsTable.client_ids.like(f"%{client_id}%"))
                .filter(ClientGroupsTable.deleted_at.is_(None))
                .order_by(ClientGroupsTable.valid_to)
                .all()
            )

        if len(client_groups) == 0:
            return False
        self.logger.warn(
            LogMsg.client_id_exists_in_group.value.format(
                client_id=client_id, group_ids=_group_ids(client_groups)
            )
        )
        return True


class GroupDeleteController:
    group_id: int
    db: db_dependency
    logger: Logger

    def __init__(self, group_id: int, db: db_dependency, logger: Logger) -> None:
        self.group_id = group_id
        self.db = db
        self.logger = logger

    def delete(self) -> None:
        client_groups: list[ClientGroupsTable] = (
            self.db.query(ClientGroupsTable)
            .filter(ClientGroupsTable.id == self.group_id)
            .filter(ClientGroupsTable.deleted_at.is_(None))
            .all()
        )

        for model in client_groups:
            model.deleted_at = datetime.now()
            self.db.add(model)

        self.db.commit()
        self.logger.info(
            LogMsg.client_group_deleted.value.format(
                client_group_id=_group_ids(client_groups),
                client_ids=_client_ids(client_groups),
            )
        )


class GroupsRespController:
    client_groups: list[ClientGroupsTable]

    def __init__(self, client_groups: list[ClientGroupsTable]) -> None:
        self.client_groups: list[ClientGroupsTable] = client_groups

    def _to_client_group(self) -> list[ClientGroup]:
        return [client_group.to_client_group() for client_group in self.client_groups]

    def resp(self) -> dict:
        return {
            AppVars.elements.value: len(self._to_client_group()),
            AppVars.group_ids.value: _group_ids(),
            AppVars.data.value: self._to_client_group(),
        }
