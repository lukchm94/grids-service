from fastapi import FastAPI

from database.main import Base, engine
from middleware.verify_token import middleware
from routers import account, auth, configs, grids, volumes

app = FastAPI()

Base.metadata.create_all(bind=engine)

# app.middleware("http")(middleware)
# TODO add the user dependencies to the middleware
app.include_router(auth.router)
app.include_router(account.router)
app.include_router(configs.router)
app.include_router(volumes.router)
# app.include_router(grids.router)
