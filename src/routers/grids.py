from fastapi import APIRouter, Path, status

from __app_configs import Paths, return_elements
from __fixtures.grids import get_all_grids
from models.grids import Grid

router = APIRouter(prefix=Paths.grids.value, tags=[Paths.grids_tag.value])


@router.get(Paths.root.value, status_code=status.HTTP_200_OK)
def read_all() -> None:
    grids: list[Grid] = get_all_grids()
    return return_elements(grids)


@router.get(Paths.root.value + "{id}", status_code=status.HTTP_200_OK)
def get_grid_by_id(id: int = Path(gt=0, lt=1000)):
    grids: list[Grid] = [grid for grid in get_all_grids() if grid.id == id]
    return return_elements(grids)
