from fastapi import APIRouter, Path, Response, status

from __app_configs import AppVars, Paths, return_elements
from controllers.configs import (
    ConfigGridController,
    ConfigModelController,
    ConfigReqController,
)
from database.main import db_dependency
from database.models import ConfigTable
from models.configs import BaseConfig, Config

router = APIRouter(prefix=Paths.configs.value, tags=[Paths.config_tag.value])


# TODO move the logic to controller


@router.get(Paths.root.value, status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency) -> None:
    configs: list[ConfigTable] = db.query(ConfigTable).all()
    return return_elements(configs)


@router.get(Paths.root.value + "{client_id}", status_code=status.HTTP_200_OK)
async def get_configs_by_client_id(db: db_dependency, client_id: int = Path(gt=0)):
    config_models: list[ConfigTable] = (
        db.query(ConfigTable).filter(ConfigTable.client_id == client_id).all()
    )
    client_configs: list[BaseConfig] = [config.to_config() for config in config_models]
    return return_elements(client_configs)


@router.get(
    Paths.root.value + "{client_id}" + Paths.grids.value, status_code=status.HTTP_200_OK
)
async def get_config_grids_by_client_id(db: db_dependency, client_id: int = Path(gt=0)):
    config_model: ConfigTable = (
        db.query(ConfigTable)
        .filter(ConfigTable.client_id == client_id)
        .order_by(ConfigTable.valid_to)
        .first()
    )
    config: Config = ConfigGridController(config_model.id, db).get_config(
        config_model.to_config()
    )
    return config


@router.post(Paths.root.value, status_code=status.HTTP_201_CREATED)
async def create_new_client_config(db: db_dependency, config_req: BaseConfig):
    req_controller: ConfigReqController = ConfigReqController(config_req)
    if req_controller.check_if_exists(db):
        return Response(
            content=AppVars.client_config_exists.value.format(
                client_id=config_req.client_id
            ),
            status_code=status.HTTP_200_OK,
        )
    valid_config_req = req_controller.format()
    config_model = ConfigTable(**valid_config_req.model_dump())
    db.add(config_model)
    db.commit()


@router.post(Paths.root.value + "{client_id}", status_code=status.HTTP_201_CREATED)
async def create_config(
    db: db_dependency, config_req: BaseConfig, client_id: int = Path(gt=0)
):
    # TODO add a middleware function to modify the request to default body to Client ID from Path
    req_controller: ConfigReqController = ConfigReqController(config_req)
    if not req_controller.check_if_exists(db):
        return Response(
            content=AppVars.no_client_config.value.format(client_id=client_id),
            status_code=status.HTTP_200_OK,
        )

    valid_config_req = req_controller.format()
    model_to_update = (
        db.query(ConfigTable)
        .filter(ConfigTable.client_id == config_req.client_id)
        .order_by(ConfigTable.valid_to)
        .first()
    )

    expired_model = ConfigModelController(model_to_update).expire(valid_config_req)
    db.add(expired_model)
    config_model = ConfigTable(**valid_config_req.model_dump())
    db.add(config_model)
    db.commit()


@router.put(Paths.root.value + "{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_config(
    db: db_dependency, config_req: BaseConfig, client_id: int = Path(gt=0)
):
    # TODO add a middleware function to modify the request to default body to Client ID from Path
    req_controller: ConfigReqController = ConfigReqController(config_req)
    if not req_controller.check_if_exists(db):
        return Response(
            content=AppVars.no_client_config.value.format(client_id=client_id),
            status_code=status.HTTP_200_OK,
        )

    valid_config_req = req_controller.format()
    model_to_update = (
        db.query(ConfigTable)
        .filter(ConfigTable.client_id == config_req.client_id)
        .order_by(ConfigTable.valid_to)
        .first()
    )
    updated_model = ConfigModelController(model_to_update).update(valid_config_req)
    # print(updated_model)
    print(updated_model.id)
    ConfigGridController(config_id=updated_model.id, db=db).check_grids(updated_model)
    print(updated_model)
    db.add(updated_model)
    db.commit()
