from fastapi import Depends, FastAPI

from __configs import Paths
from __fixtures.configs import config_with_volume_grid
from models.configs import Config
from models.grids import Grid

app = FastAPI()

print(type(app))


@app.get(Paths.root.value)
def read_root() -> None:
    return "Hello from route"


# @app.get(Paths.grids.value)
# def read_grid() -> None:
#     grids = Grid()
#     return grids.to_str()


@app.get(Paths.configs.value)
def read_config() -> None:
    configs: Config = config_with_volume_grid()
    return {
        "id": configs.client_id,
        "valid": configs.is_valid(),
        "data": configs,
        "dict": configs.model_dump_json(),
    }
