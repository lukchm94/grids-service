from fastapi import APIRouter, Path, status

from __app_configs import Paths, return_elements
from controllers.grids import (
    DiscGridReqController,
    PeakGridReqController,
    VolGridReqController,
)
from database.main import db_dependency
from database.models import DiscountGridTable, PeakGridTable, VolumeGridTable
from models.grids import DiscountGrid, PeakOffPeakGrid, VolumeGrid

router = APIRouter(prefix=Paths.grids.value, tags=[Paths.grids_tag.value])


@router.get(Paths.root.value, status_code=status.HTTP_200_OK)
async def get_all_grids(db: db_dependency):
    vol_grids: list[VolumeGridTable] = db.query(VolumeGridTable).all()
    peak_grids: list[PeakGridTable] = db.query(PeakGridTable).all()
    discount_grids: list[DiscountGridTable] = db.query(DiscountGridTable).all()
    return return_elements(vol_grids + peak_grids + discount_grids)


@router.get(Paths.volume.value, status_code=status.HTTP_200_OK)
async def get_all_volume_grids(db: db_dependency) -> None:
    grids: list[VolumeGridTable] = db.query(VolumeGridTable).all()
    return return_elements(grids)


@router.get(Paths.peak.value, status_code=status.HTTP_200_OK)
async def get_all_peak_grids(db: db_dependency) -> None:
    grids: list[PeakGridTable] = db.query(PeakGridTable).all()
    return return_elements(grids)


@router.get(Paths.discount.value, status_code=status.HTTP_200_OK)
async def get_all_discount_grids(db: db_dependency) -> None:
    grids: list[DiscountGridTable] = db.query(DiscountGridTable).all()
    return return_elements(grids)


# Getting grids by grid_id
@router.get(Paths.volume.value + "/{id}", status_code=status.HTTP_200_OK)
async def get_volume_grid_by_id(db: db_dependency, id: int = Path(gt=0)) -> None:
    grids_models: list[VolumeGridTable] = (
        db.query(VolumeGridTable).filter(VolumeGridTable.id == id).all()
    )
    grids: list[VolumeGrid] = [grid.to_grid() for grid in grids_models]
    return return_elements(grids)


@router.get(Paths.peak.value + "/{id}", status_code=status.HTTP_200_OK)
async def get_peak_grids_by_id(db: db_dependency, id: int = Path(gt=0)) -> None:
    grids_models: list[PeakGridTable] = (
        db.query(PeakGridTable).filter(PeakGridTable.id == id).all()
    )
    grids: list[PeakOffPeakGrid] = [grid.to_grid() for grid in grids_models]
    return return_elements(grids)


@router.get(Paths.discount.value + "/{id}", status_code=status.HTTP_200_OK)
async def get_discount_grids_by_id(db: db_dependency, id: int = Path(gt=0)) -> None:
    grids_models: list[DiscountGridTable] = (
        db.query(DiscountGridTable).filter(DiscountGridTable.id == id).all()
    )
    grids: list[DiscountGrid] = [grid.to_grid() for grid in grids_models]
    return return_elements(grids)


# Create Grid elements
@router.post(Paths.create_vol.value + "{id}", status_code=status.HTTP_201_CREATED)
async def create_volume_grid(
    db: db_dependency, grid_req: VolumeGrid, id: int = Path(gt=0)
) -> None:
    grid_model_req = VolGridReqController(grid_req).to_grid_req_model(id)
    # TODO validate that the grid_req has a valid configuration and the configuration is of volume / fee type
    grid_model = VolumeGridTable(**grid_model_req.model_dump())
    db.add(grid_model)
    db.commit()


@router.post(Paths.create_peak.value + "{id}", status_code=status.HTTP_201_CREATED)
async def create_peak_grid(
    db: db_dependency, grid_req: PeakOffPeakGrid, id: int = Path(gt=0)
) -> None:
    grid_model_req = PeakGridReqController(grid_req).to_grid_req_model(id)
    # TODO validate that the grid_req has a valid configuration and the configuration is of peak / fee type
    grid_model = PeakGridTable(**grid_model_req.model_dump())
    db.add(grid_model)
    db.commit()


@router.post(Paths.create_disc.value + "{id}", status_code=status.HTTP_201_CREATED)
async def create_discount_grid(
    db: db_dependency, grid_req: DiscountGrid, id: int = Path(gt=0)
) -> None:
    grid_model_req = DiscGridReqController(grid_req).to_grid_req_model(id)
    # TODO validate that the grid_req has a valid configuration and the configuration is of volume / discount type
    grid_model = DiscountGridTable(**grid_model_req.model_dump())
    db.add(grid_model)
    db.commit()
