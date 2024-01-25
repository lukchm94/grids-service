from fastapi import FastAPI

from __configs import Paths
from models.configs import Config
from models.grids import Grid

app = FastAPI()

print(type(app))


@app.get(Paths.root.value)
def read_root() -> None:
    return "Hello from route"


@app.get(Paths.grids.value)
def read_grid() -> None:
    grids = Grid()
    return grids.to_str()


@app.get(Paths.configs.value)
def read_config() -> None:
    configs = Config()
    return configs.to_str()
