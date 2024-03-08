from fastapi import APIRouter, Path, Response, status
from sqlalchemy import desc

from __app_configs import AppVars, Paths, return_elements
from controllers.configs import (
    ConfigGridController,
    ConfigModelController,
    ConfigReqController,
)
from controllers.grids import ConfigGridReqController
from database.main import db_dependency
from database.models import (
    ConfigTable,
    DiscountGridTable,
    PeakGridTable,
    VolumeGridTable,
)
from models.configs import BaseConfig, Config
from models.grids import DiscountGridReq, PeakGridReq, VolumeGridReq

router = APIRouter(prefix=Paths.configs.value, tags=[Paths.config_tag.value])


# TODO move the logic to controller


@router.get(Paths.root.value, status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency) -> None:
    configs: list[ConfigTable] = db.query(ConfigTable).all()
    return return_elements(configs)


@router.get(Paths.get_all_config.value + "{client_id}", status_code=status.HTTP_200_OK)
async def get_configs_by_client_id(db: db_dependency, client_id: int = Path(gt=0)):
    config_models: list[ConfigTable] = (
        db.query(ConfigTable).filter(ConfigTable.client_id == client_id).all()
    )
    client_configs: list[Config] = [
        ConfigGridController(model.id, db).get_config(model.to_config())
        for model in config_models
    ]
    return return_elements(client_configs)


@router.get(Paths.get_last_config.value + "{client_id}", status_code=status.HTTP_200_OK)
async def get_last_config_with_grids_by_client_id(
    db: db_dependency, client_id: int = Path(gt=0)
):
    config_model: ConfigTable = (
        db.query(ConfigTable)
        .filter(ConfigTable.client_id == client_id)
        .order_by(desc(ConfigTable.valid_to))
        .first()
    )
    config: Config = ConfigGridController(config_model.id, db).get_config(
        config_model.to_config()
    )
    return config


@router.put(Paths.root.value + "{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_last_config(
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
    ConfigGridController(config_id=updated_model.id, db=db).check_grids(updated_model)
    db.add(updated_model)
    db.commit()


@router.post(Paths.grids.value, status_code=status.HTTP_201_CREATED)
async def create_config_with_grids(db: db_dependency, config_req: Config):
    # TODO add a middleware function to modify the request to default body to Client ID from Path
    req_controller: ConfigReqController = ConfigReqController(config_req)
    if not req_controller.check_if_exists(db):
        return Response(
            content=AppVars.no_client_config.value.format(
                client_id=config_req.client_id
            ),
            status_code=status.HTTP_200_OK,
        )

    valid_config_req = req_controller.format()
    model_to_expire = (
        db.query(ConfigTable)
        .filter(ConfigTable.client_id == config_req.client_id)
        .order_by(ConfigTable.valid_to)
        .first()
    )

    expired_model = ConfigModelController(model_to_expire).expire(valid_config_req)
    print(expired_model)
    db.add(expired_model)
    config_model = ConfigTable(**valid_config_req.model_dump())
    print(config_model)
    db.add(config_model)

    last_config = db.query(ConfigTable).order_by(desc(ConfigTable.id)).first()

    grids_req = ConfigGridReqController(req=config_req, id=last_config.id + 1).format()
    for grid in grids_req:
        if isinstance(grid, VolumeGridReq):
            grid_model = VolumeGridTable(**grid.model_dump())
        elif isinstance(grid, PeakGridReq):
            grid_model = PeakGridTable(**grid.model_dump())
        elif isinstance(grid, DiscountGridReq):
            grid_model = DiscountGridTable(**grid.model_dump())

        if grid_model is not None:
            print(grid_model)
            db.add(grid_model)

    db.commit()
