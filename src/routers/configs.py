from logging import Logger

from fastapi import APIRouter, Path, Response, status
from sqlalchemy import desc

from __app_configs import AppVars, LogMsg, Paths, return_elements
from controllers.configs import (
    ConfigModelController,
    ConfigReqController,
    ConfigRespController,
)
from controllers.grids import GridDeleteController, GridReqController
from database.main import db_dependency
from database.models import ConfigTable
from models.configs import BaseConfig, Config
from utils.logger import get_cloudwatch_logger

logger: Logger = get_cloudwatch_logger()
router = APIRouter(prefix=Paths.configs.value, tags=[Paths.config_tag.value])


@router.get(Paths.all_config.value + "{client_id}", status_code=status.HTTP_200_OK)
async def get_configs_by_client_id(db: db_dependency, client_id: int = Path(gt=0)):
    config_models: list[ConfigTable] = (
        db.query(ConfigTable).filter(ConfigTable.client_id == client_id).all()
    )
    if len(config_models) == 0:
        logger.info(AppVars.no_client_config.value.format(client_id=client_id))
        return Response(
            content=AppVars.no_client_config.value.format(client_id=client_id),
            status_code=status.HTTP_200_OK,
        )

    client_configs: list[Config] = [
        ConfigRespController(model.id, db).get_config(model.to_config())
        for model in config_models
    ]
    return return_elements(client_configs)


@router.get(Paths.last_config.value + "{client_id}", status_code=status.HTTP_200_OK)
async def get_last_config_with_grids_by_client_id(
    db: db_dependency, client_id: int = Path(gt=0)
):
    config_model: ConfigTable = (
        db.query(ConfigTable)
        .filter(ConfigTable.client_id == client_id)
        .order_by(desc(ConfigTable.valid_to))
        .first()
    )
    if config_model is None:
        logger.info(AppVars.no_client_config.value.format(client_id=client_id))
        return Response(
            content=AppVars.no_client_config.value.format(client_id=client_id),
            status_code=status.HTTP_200_OK,
        )

    config: Config = ConfigRespController(config_model.id, db).get_config(
        config_model.to_config()
    )
    return config


@router.put(Paths.root.value + "{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_last_config(
    db: db_dependency, config_req: BaseConfig, client_id: int = Path(gt=0)
):
    # TODO add a middleware function to modify the request to default body to Client ID from Path
    config_req.client_id = client_id
    req_controller: ConfigReqController = ConfigReqController(config_req)
    if not req_controller.check_if_exists(db):
        logger.info(AppVars.no_client_config.value.format(client_id=client_id))
        return Response(
            content=AppVars.no_client_config.value.format(client_id=client_id),
            status_code=status.HTTP_200_OK,
        )

    valid_config_req = req_controller.format()
    model_to_update = (
        db.query(ConfigTable)
        .filter(ConfigTable.client_id == config_req.client_id)
        .order_by(desc(ConfigTable.valid_to))
        .first()
    )
    updated_model = ConfigModelController(model_to_update).update(valid_config_req)
    ConfigRespController(config_id=updated_model.id, db=db).check_grids(updated_model)
    db.add(updated_model)
    db.commit()
    logger.info(
        LogMsg.config_updated.value.format(
            config_id=updated_model.id, client_id=updated_model.client_id
        )
    )


@router.post(Paths.grids.value, status_code=status.HTTP_201_CREATED)
async def create_config_with_grids(db: db_dependency, config_req: Config):
    # TODO add a middleware function to modify the request to default body to Client ID from Path
    req_controller: ConfigReqController = ConfigReqController(config_req)
    valid_config_req = req_controller.format()
    if req_controller.check_if_exists(db):
        model_to_expire = (
            db.query(ConfigTable)
            .filter(ConfigTable.client_id == config_req.client_id)
            .order_by(ConfigTable.valid_to)
            .first()
        )
        expired_model = ConfigModelController(model_to_expire).expire(valid_config_req)
        db.add(expired_model)
        logger.info(
            LogMsg.config_expired.value.format(
                config_id=expired_model.id,
                client_id=expired_model.client_id,
                expire_date=expired_model.valid_to,
            )
        )

    config_model = ConfigTable(**valid_config_req.model_dump())
    db.add(config_model)
    db.commit()
    logger.info(
        LogMsg.config_created.value.format(
            config_id=config_model.id, client_id=config_model.client_id
        )
    )
    last_config = db.query(ConfigTable).order_by(desc(ConfigTable.id)).first()

    GridReqController(req=config_req, id=last_config.id).upload()
    db.commit()
    logger.info(
        LogMsg.grids_created.value.format(
            config_id=config_model.id, client_id=config_model.client_id
        )
    )


@router.delete(Paths.all_config.value + "{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_config(db: db_dependency, id: int = Path(gt=0)):
    models_to_delete = db.query(ConfigTable).filter(ConfigTable.client_id == id).all()
    if len(models_to_delete) == 0:
        logger.info(AppVars.no_client_config.value.format(client_id=id))
        return Response(
            content=AppVars.no_client_config.value.format(client_id=id),
            status_code=status.HTTP_200_OK,
        )

    for model in models_to_delete:
        GridDeleteController(model, db).delete()
        logger.info(
            LogMsg.grids_deleted.value.format(
                config_id=model.id, client_id=model.client_id
            )
        )

    db.query(ConfigTable).filter(ConfigTable.client_id == id).delete()
    db.commit()
    logger.info(
        LogMsg.config_deleted.value.format(
            config_id=[config.id for config in models_to_delete],
            client_id=[config.client_id for config in models_to_delete],
        )
    )


@router.delete(Paths.last_config.value + "{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_last_config(db: db_dependency, id: int = Path(gt=0)):
    model_to_delete = (
        db.query(ConfigTable)
        .filter(ConfigTable.client_id == id)
        .order_by(desc(ConfigTable.valid_to))
        .first()
    )

    if model_to_delete is None:
        logger.info(AppVars.no_client_config.value.format(client_id=id))
        return Response(
            content=AppVars.no_client_config.value.format(client_id=id),
            status_code=status.HTTP_200_OK,
        )

    GridDeleteController(model_to_delete, db).delete()
    logger.info(
        LogMsg.grids_deleted.value.format(
            config_id=model_to_delete.id, client_id=model_to_delete.client_id
        )
    )

    db.query(ConfigTable).filter(ConfigTable.client_id == id).filter(
        ConfigTable.id == model_to_delete.id
    ).delete()
    db.commit()
    logger.info(
        LogMsg.config_deleted.value.format(
            config_id=model_to_delete.id, client_id=model_to_delete.client_id
        )
    )
