from fastapi import FastAPI

from __app_configs import AppVars, Paths
from routers import configs, grids

app = FastAPI()

app.include_router(configs.router)
app.include_router(grids.router)


@app.get(Paths.root.value)
def read_root() -> None:
    return AppVars.hello.value
