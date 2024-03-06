from fastapi import APIRouter, Path, status

from __app_configs import Paths, return_elements
from controllers.configs import ConfigReqController
from database.main import db_dependency
from database.models import ConfigTable
from models.configs import BaseConfig

router = APIRouter(prefix=Paths.configs.value, tags=[Paths.config_tag.value])


@router.get(Paths.root.value, status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency) -> None:
    configs: list[ConfigTable] = db.query(ConfigTable).all()
    return return_elements(configs)


@router.get(Paths.root.value + "{client_id}", status_code=status.HTTP_200_OK)
async def get_config_by_client_id(db: db_dependency, client_id: int = Path(gt=0)):
    config_models: list[ConfigTable] = (
        db.query(ConfigTable).filter(ConfigTable.client_id == client_id).all()
    )
    client_configs: list[BaseConfig] = [config.to_config() for config in config_models]
    return return_elements(client_configs)


@router.get(Paths.root.value + "{client_id}", status_code=status.HTTP_200_OK)
async def get_config_with_grids_by_client_id(
    db: db_dependency, client_id: int = Path(gt=0)
):
    config_models: list[ConfigTable] = (
        db.query(ConfigTable).filter(ConfigTable.client_id == client_id).all()
    )
    client_configs: list[BaseConfig] = [config.to_config() for config in config_models]
    return return_elements(client_configs)


@router.post(Paths.root.value, status_code=status.HTTP_201_CREATED)
async def create_config(db: db_dependency, config_req: BaseConfig):
    valid_config_req = ConfigReqController(config_req).format()
    config_model = ConfigTable(**valid_config_req.model_dump())
    db.add(config_model)
    db.commit()
