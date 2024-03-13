from fastapi import APIRouter, Path, status

from __app_configs import Paths, return_elements
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
