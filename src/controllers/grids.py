from __future__ import annotations

from typing import Union

from __app_configs import (
    Deliminator,
    GridsValidationTypes,
    PricingImplementationTypes,
    PricingTypes,
)
from __exceptions import GridsValuesError
from models.configs import Config
from models.grids import (
    DiscountGrid,
    DiscountGridReq,
    PeakGridReq,
    PeakOffPeakGrid,
    VolumeGrid,
    VolumeGridReq,
)


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
            weekday_option=Deliminator.comma.value.join(
                [str(day) for day in self.grid_req.weekday_option]
            ),
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


class GridReqController:
    req: Config
    id: int

    def __init__(self, req: Config, id: int) -> GridReqController:
        self.req = req
        self.id = id

    def _order_grids(
        self, grids: Union[list[VolumeGrid], list[PeakOffPeakGrid], list[DiscountGrid]]
    ) -> Union[list[VolumeGrid], list[PeakOffPeakGrid], list[DiscountGrid]]:
        return sorted(
            grids,
            key=lambda grid: (grid.min_volume_threshold, grid.min_distance_in_unit),
        )

    def _validate_grids(
        self, grids: Union[list[VolumeGrid], list[PeakOffPeakGrid], list[DiscountGrid]]
    ) -> Union[list[VolumeGrid], list[PeakOffPeakGrid], list[DiscountGrid]]:
        ordered_grids = self._order_grids(grids)

        vol_min: int = len(set([grid.min_volume_threshold for grid in ordered_grids]))
        vol_max: int = len(set([grid.min_volume_threshold for grid in ordered_grids]))

        if vol_max != vol_min:
            raise GridsValuesError(
                client_id=self.req.client_id, type=GridsValidationTypes.vol.value
            )

        dist_min: int = len(set([grid.min_distance_in_unit for grid in ordered_grids]))
        dist_max: int = len(set([grid.max_distance_in_unit for grid in ordered_grids]))

        if dist_max != dist_min:
            raise GridsValuesError(
                client_id=self.req.client_id, type=GridsValidationTypes.dist.value
            )

        expected_grids_len: int = vol_min * dist_min

        if expected_grids_len != len(ordered_grids):
            raise GridsValuesError(
                client_id=self.req.client_id, type=GridsValidationTypes.totals.value
            )

        return ordered_grids

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
        """
        The `format` function returns a list of grid requests after formatting and validating them.
        :return: A list of either VolumeGridReq, PeakGridReq, or DiscountGridReq, depending on the type
        of grid requests obtained from the input grids.
        """

        grids = self._get_grid_req(self.req.grids)
        return self._validate_grids(grids)
