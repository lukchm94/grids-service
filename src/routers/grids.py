from fastapi import APIRouter, Path, status

from __app_configs import Paths, return_elements
from database.main import db_dependency
from database.models import BaseGrid, Grid
from models.grids import BaseGridRequest, GridRequest

router = APIRouter(prefix=Paths.grids.value, tags=[Paths.grids_tag.value])


@router.get(Paths.root.value, status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency) -> None:
    grids: list[Grid] = db.query(Grid).all()
    return return_elements(grids)


# TODO separate Grids into Peak, Volume and Discount Grids
@router.get(Paths.root.value + "base", status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency) -> None:
    grids: list[BaseGrid] = db.query(BaseGrid).all()
    return return_elements(grids)


@router.get(Paths.root.value + "{id}", status_code=status.HTTP_200_OK)
async def get_grid_by_id(db: db_dependency, id: int = Path(gt=0, lt=1000)):
    grids: list[Grid] = db.query(Grid).filter(Grid.id == id)
    return return_elements(grids)


@router.post(Paths.root.value + "create", status_code=status.HTTP_201_CREATED)
async def create_grid(db: db_dependency, grid_req: GridRequest):
    print(grid_req)
    grid_model = Grid(**grid_req.model_dump())
    print(grid_model)
    db.add(grid_model)
    db.commit()


@router.post(Paths.root.value + "create/base", status_code=status.HTTP_201_CREATED)
async def create_grid(db: db_dependency, grid_req: BaseGridRequest):
    print(grid_req)
    grid_model = BaseGrid(**grid_req.model_dump())
    print(grid_model)
    db.add(grid_model)
    db.commit()
