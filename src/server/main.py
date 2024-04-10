from fastapi import FastAPI

from database.main import Base, engine
from routers import account, auth, configs, users, volumes

app = FastAPI()

Base.metadata.create_all(bind=engine)

# TODO add the user dependencies to the middleware
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(account.router)
app.include_router(configs.router)
app.include_router(volumes.router)
# app.include_router(grids.router)
