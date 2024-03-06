from __future__ import annotations

from models.grids import (
    DiscountGrid,
    DiscountGridRequest,
    PeakGridRequest,
    PeakOffPeakGrid,
    VolumeGrid,
    VolumeGridRequest,
)


class VolGridReqController:
    grid_req: VolumeGrid

    def __init__(self, grid_req: VolumeGrid) -> VolGridReqController:
        self.grid_req = grid_req

    def to_grid_req_model(self, config_id: int) -> VolumeGridRequest:
        return VolumeGridRequest(
            config_id=config_id,
            min_volume_threshold=self.grid_req.min_volume_threshold,
            max_volume_threshold=self.grid_req.max_volume_threshold,
            min_distance_in_unit=self.grid_req.min_distance_in_unit,
            max_distance_in_unit=self.grid_req.max_distance_in_unit,
            pickup_amount=self.grid_req.pickup_amount,
            distance_amount_per_unit=self.grid_req.distance_amount_per_unit,
            dropoff_amount=self.grid_req.dropoff_amount,
        )


class PeakGridReqController:
    grid_req: PeakOffPeakGrid

    def __init__(self, grid_req: PeakOffPeakGrid) -> PeakGridReqController:
        self.grid_req = grid_req

    def to_grid_req_model(self, config_id: int) -> PeakGridRequest:
        return PeakGridRequest(
            config_id=config_id,
            min_volume_threshold=self.grid_req.min_volume_threshold,
            max_volume_threshold=self.grid_req.max_volume_threshold,
            min_distance_in_unit=self.grid_req.min_distance_in_unit,
            max_distance_in_unit=self.grid_req.max_distance_in_unit,
            pickup_amount=self.grid_req.pickup_amount,
            distance_amount_per_unit=self.grid_req.distance_amount_per_unit,
            dropoff_amount=self.grid_req.dropoff_amount,
            weekday_option=self.grid_req.weekday_option,
            hour_start=self.grid_req.hour_start,
            hour_end=self.grid_req.hour_end,
        )


class DiscGridReqController:
    grid_req: DiscountGrid

    def __init__(self, grid_req: DiscountGrid) -> DiscGridReqController:
        self.grid_req = grid_req

    def to_grid_req_model(self, config_id: int) -> DiscountGridRequest:
        return DiscountGridRequest(
            config_id=config_id,
            min_volume_threshold=self.grid_req.min_volume_threshold,
            max_volume_threshold=self.grid_req.max_volume_threshold,
            min_distance_in_unit=self.grid_req.min_distance_in_unit,
            max_distance_in_unit=self.grid_req.max_distance_in_unit,
            discount_amount=self.grid_req.discount_amount,
        )
