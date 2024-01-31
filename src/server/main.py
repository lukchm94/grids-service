from fastapi import FastAPI

from __app_configs import AppVars, Paths
from database.main import Base, engine, get_db
from routers import configs, grids

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(configs.router)
app.include_router(grids.router)


@app.get(Paths.root.value)
def read_root() -> None:
    return AppVars.hello.value
