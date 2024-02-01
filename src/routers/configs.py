from fastapi import APIRouter, Path, status

from __app_configs import Paths, return_elements
from database.main import db_dependency
from database.models import Config
from models.configs import ConfigRequest

router = APIRouter(prefix=Paths.configs.value, tags=[Paths.config_tag.value])


@router.get(Paths.root.value, status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency) -> None:
    configs: list[Config] = db.query(Config)
    return return_elements(configs)


@router.get(Paths.root.value + "{id}", status_code=status.HTTP_200_OK)
async def get_config_by_id(db: db_dependency, id: int = Path(gt=0, lt=1000)):
    client_config: list[Config] = db.query(Config).filter(Config.client_id == id)
    return return_elements(client_config)


@router.post(Paths.root.value, status_code=status.HTTP_201_CREATED)
async def create_config(db: db_dependency, config_req: ConfigRequest):
    config_model = Config(**config_req.model_dump())
    db.add(config_model)
    db.commit()
