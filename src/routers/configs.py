from fastapi import APIRouter, Path, status

from __app_configs import Paths, return_elements
from __fixtures.configs import get_all_configs
from models.configs import Config

router = APIRouter(prefix=Paths.configs.value, tags=[Paths.config_tag.value])


@router.get(Paths.root.value, status_code=status.HTTP_200_OK)
def read_all() -> None:
    configs: list[Config] = get_all_configs()
    return return_elements(configs)


@router.get(Paths.root.value + "{id}", status_code=status.HTTP_200_OK)
def get_config_by_id(id: int = Path(gt=0, lt=1000)):
    configs: list[Config] = get_all_configs()
    client_config: list[Config] = [
        config for config in configs if config.client_id == id
    ]
    return return_elements(client_config)
