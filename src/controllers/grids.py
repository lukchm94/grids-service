from __future__ import annotations

from typing import Union

from __app_configs import Deliminator, PricingImplementationTypes, PricingTypes
from models.configs import Config
from models.grids import (
    DiscountGrid,
    DiscountGridReq,
    PeakGridReq,
    PeakOffPeakGrid,
    VolumeGrid,
    VolumeGridReq,
)


# TODO organize the the controller better
class VolGridReqController:
    grid_req: VolumeGrid

    def __init__(self, grid_req: VolumeGrid) -> VolGridReqController:
        self.grid_req = grid_req

    def to_grid_req_model(self, config_id: int) -> VolumeGridReq:
        return VolumeGridReq(
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

    def to_grid_req_model(self, config_id: int) -> PeakGridReq:
        return PeakGridReq(
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

    def to_grid_req_model(self, config_id: int) -> DiscountGridReq:
        return DiscountGridReq(
            config_id=config_id,
            min_volume_threshold=self.grid_req.min_volume_threshold,
            max_volume_threshold=self.grid_req.max_volume_threshold,
            min_distance_in_unit=self.grid_req.min_distance_in_unit,
            max_distance_in_unit=self.grid_req.max_distance_in_unit,
            discount_amount=self.grid_req.discount_amount,
        )


class ConfigGridReqController:
    req: Config
    id: int

    def __init__(self, req: Config, id: int) -> ConfigGridReqController:
        self.req = req
        self.id = id

    def _get_grid_req(
        self, grids: Union[list[VolumeGrid], list[PeakOffPeakGrid], list[DiscountGrid]]
    ) -> Union[list[VolumeGridReq], list[PeakGridReq], list[DiscountGridReq]]:

        if (
            self.req.config_type == PricingImplementationTypes.discount.value
            and self.req.pricing_type == PricingTypes.volume.value
        ):
            return [
                DiscGridReqController(grid).to_grid_req_model(self.id) for grid in grids
            ]

        elif (
            self.req.config_type == PricingImplementationTypes.fee.value
            and self.req.pricing_type == PricingTypes.peak.value
        ):
            return [
                PeakGridReqController(grid).to_grid_req_model(self.id) for grid in grids
            ]

        elif (
            self.req.config_type == PricingImplementationTypes.fee.value
            and self.req.pricing_type == PricingTypes.volume.value
        ):
            return [
                VolGridReqController(grid).to_grid_req_model(self.id) for grid in grids
            ]

    def format(
        self,
    ) -> Union[list[VolumeGridReq], list[PeakGridReq], list[DiscountGridReq]]:
        # TODO here the logic should validate if each new grid is okay
        # and if each grid is ordered correctly (grid for vol 1 bucket (distances buckets), etc)
        return self._get_grid_req(self.req.grids)
