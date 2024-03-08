from fastapi import FastAPI

from database.main import Base, engine
from routers import configs, grids

app = FastAPI()

Base.metadata.create_all(bind=engine)

# TODO update the Configs objects for the company_name and frequency
app.include_router(configs.router)
app.include_router(grids.router)
