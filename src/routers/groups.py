from logging import Logger

from fastapi import APIRouter, Path, Response, status
from sqlalchemy import desc

from __app_configs import LogMsg, Paths, return_elements
from controllers.groups import (
    GroupDeleteController,
    GroupReqController,
    GroupsRespController,
)
from database.main import db_dependency
from database.models import ClientGroupsTable
from models.groups import ClientGroup
from utils.logger import get_cloudwatch_logger

logger: Logger = get_cloudwatch_logger()
router = APIRouter(prefix=Paths.groups.value, tags=[Paths.group_tag.value])


@router.get(
    Paths.all_groups_by_client.value + "{client_id}", status_code=status.HTTP_200_OK
)
async def get_all_client_groups_by_client_id(
    db: db_dependency, client_id: int = Path(gt=0)
):
    client_group_models: list[ClientGroupsTable] = (
        db.query(ClientGroupsTable)
        .filter(ClientGroupsTable.client_ids.like(f"%{client_id}%"))
        .filter(ClientGroupsTable.deleted_at.is_(None))
        .order_by(desc(ClientGroupsTable.valid_to))
        .all()
    )

    if len(client_group_models) == 0:
        return Response(
            content=LogMsg.missing_group.value,
            status_code=status.HTTP_200_OK,
        )

    return GroupsRespController(client_group_models).resp()


@router.get(Paths.all_groups.value + "{group_id}", status_code=status.HTTP_200_OK)
async def get_all_client_groups_by_group_id(
    db: db_dependency, group_id: int = Path(gt=0)
):
    client_group_models: list[ClientGroupsTable] = (
        db.query(ClientGroupsTable)
        .filter(ClientGroupsTable.id == group_id)
        .order_by(desc(ClientGroupsTable.valid_to))
        .all()
    )

    if len(client_group_models) == 0:
        return Response(
            content=LogMsg.missing_group.value,
            status_code=status.HTTP_200_OK,
        )
    client_groups: list[ClientGroup] = [
        model.to_client_group() for model in client_group_models
    ]
    return return_elements(client_groups)


@router.get(Paths.last_group.value + "{group_id}", status_code=status.HTTP_200_OK)
async def get_last_client_groups_by_group_id(
    db: db_dependency, group_id: int = Path(gt=0)
):
    client_group_model: ClientGroupsTable = (
        db.query(ClientGroupsTable)
        .filter(ClientGroupsTable.deleted_at.is_(None))
        .filter(ClientGroupsTable.id == group_id)
        .order_by(desc(ClientGroupsTable.valid_to))
        .first()
    )

    if client_group_model is None:
        return Response(
            content=LogMsg.missing_group.value,
            status_code=status.HTTP_200_OK,
        )

    return client_group_model.to_client_group()


@router.post(Paths.root.value, status_code=status.HTTP_201_CREATED)
async def create_client_group(db: db_dependency, client_group_req: ClientGroup):
    req_controller = GroupReqController(client_group_req, logger)
    if req_controller.check_if_exists(db):
        return Response(
            content=LogMsg.client_id_in_group.value,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    valid_req = req_controller.format()
    client_group_model = ClientGroupsTable(**valid_req.model_dump())
    db.add(client_group_model)
    db.commit()
    last_group = (
        db.query(ClientGroupsTable).order_by(desc(ClientGroupsTable.id)).first()
    )
    logger.info(
        LogMsg.client_group_created.value.format(
            client_group_id=last_group.id, client_ids=client_group_model.client_ids
        )
    )


@router.put(Paths.delete_group.value + "{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client_group(db: db_dependency, id: int = Path(gt=0)):
    try:
        delete_controller = GroupDeleteController(id, db, logger)
        delete_controller.delete()
    except Exception as err:
        logger.error(err)
