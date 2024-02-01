import sys
from pathlib import Path

from fastapi import FastAPI

sys.path.insert(1, str(Path(__file__).parents[1]))
from database.main import Base, engine
from routers import configs, grids

app = FastAPI()

Base.metadata.create_all(bind=engine)


app.include_router(configs.router)
app.include_router(grids.router)
