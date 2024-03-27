from fastapi import FastAPI

from database.main import Base, engine
from routers import account, configs, grids, volumes

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(account.router)
app.include_router(configs.router)
app.include_router(grids.router)
app.include_router(volumes.router)
