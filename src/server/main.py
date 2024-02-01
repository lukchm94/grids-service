import sys
from pathlib import Path

from fastapi import FastAPI

sys.path.insert(1, str(Path(__file__).parents[1]))
from __app_configs import Paths
from database.main import Base, db_dependency, engine

# from database.models import Config, Grid
from routers import configs, grids

app = FastAPI()

Base.metadata.create_all(bind=engine)


app.include_router(configs.router)
app.include_router(grids.router)


@app.get(Paths.root.value)
async def read_root(db: db_dependency) -> None:
    return "HELLO"
