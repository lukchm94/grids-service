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


@router.get(Paths.root.value + "volume", status_code=status.HTTP_200_OK)
async def get_all_volume_grids(db: db_dependency) -> None:
    grids: list[VolumeGridTable] = db.query(VolumeGridTable).all()
    return return_elements(grids)


@router.get(Paths.root.value + "peak", status_code=status.HTTP_200_OK)
async def get_all_volume_grids(db: db_dependency) -> None:
    grids: list[PeakGridTable] = db.query(PeakGridTable).all()
    return return_elements(grids)


@router.get(Paths.root.value + "discount", status_code=status.HTTP_200_OK)
async def get_all_volume_grids(db: db_dependency) -> None:
    grids: list[DiscountGridTable] = db.query(DiscountGridTable).all()
    return return_elements(grids)


@router.post(Paths.root.value + "create/volume", status_code=status.HTTP_201_CREATED)
async def create_volume_grid(db: db_dependency, grid_req: VolumeGrid) -> None:
    grid_model = VolumeGridTable(**grid_req.model_dump())
    db.add(grid_model)
    db.commit()


@router.post(Paths.root.value + "create/peak", status_code=status.HTTP_201_CREATED)
async def create_peak_grid(db: db_dependency, grid_req: PeakOffPeakGrid) -> None:
    grid_model = PeakGridTable(**grid_req.model_dump())
    db.add(grid_model)
    db.commit()


@router.post(Paths.root.value + "create/discount", status_code=status.HTTP_201_CREATED)
async def create_discount_grid(db: db_dependency, grid_req: DiscountGrid) -> None:
    grid_model = DiscountGridTable(**grid_req.model_dump())
    db.add(grid_model)
    db.commit()
