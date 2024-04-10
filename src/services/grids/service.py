from __future__ import annotations

from logging import Logger
from typing import Union

from __app_configs import (
    Deliminator,
    GridsValidationTypes,
    LogMsg,
    PricingImplementationTypes,
    PricingTypes,
)
from __exceptions import ConfigGridValidationError, GridsValuesError
from database.main import db_dependency
from database.models import (
    ConfigTable,
    DiscountGridTable,
    PeakGridTable,
    VolumeGridTable,
)
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
        vol_max: int = len(set([grid.max_volume_threshold for grid in ordered_grids]))

        if vol_max != vol_min:
            raise GridsValuesError(type=GridsValidationTypes.vol.value)

        dist_min: int = len(set([grid.min_distance_in_unit for grid in ordered_grids]))
        dist_max: int = len(set([grid.max_distance_in_unit for grid in ordered_grids]))

        if dist_max != dist_min:
            raise GridsValuesError(type=GridsValidationTypes.dist.value)

        expected_grids_len: int = vol_min * dist_min

        if expected_grids_len != len(ordered_grids):
            raise GridsValuesError(type=GridsValidationTypes.totals.value)

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

    def _format(
        self,
    ) -> Union[list[VolumeGridReq], list[PeakGridReq], list[DiscountGridReq]]:
        """
        The `format` function returns a list of grid requests after formatting and validating them.
        :return: A list of either VolumeGridReq, PeakGridReq, or DiscountGridReq, depending on the type
        of grid requests obtained from the input grids.
        """

        grids = self._get_grid_req(self.req.grids)
        return self._validate_grids(grids)

    def upload(self, db: db_dependency) -> None:
        """
        This function uploads different types of grid data to a database based on their respective
        types.

        :param db: The `db` parameter in the `upload` method is of type `db_dependency`, which is likely
        a dependency representing a database connection or session that is used to interact with the
        database. This parameter is used to add instances of different grid models (VolumeGridTable,
        PeakGridTable, DiscountGrid
        :type db: db_dependency
        """
        grids_req = self._format()
        for grid in grids_req:
            if isinstance(grid, VolumeGridReq):
                grid_model = VolumeGridTable(**grid.model_dump())
            elif isinstance(grid, PeakGridReq):
                grid_model = PeakGridTable(**grid.model_dump())
            elif isinstance(grid, DiscountGridReq):
                grid_model = DiscountGridTable(**grid.model_dump())

            if grid_model is not None:
                db.add(grid_model)


class GridDeleteController:
    db: db_dependency
    config_id: int
    config_type: str
    pricing_type: str
    logger: Logger

    def __init__(
        self, config_model: ConfigTable, db: db_dependency, logger: Logger
    ) -> GridDeleteController:
        self.config_id = config_model.id
        self.config_type = config_model.config_type
        self.pricing_type = config_model.pricing_type
        self.db = db
        self.logger = logger

    def _log(self) -> None:
        self.logger.info(LogMsg.grids_deleted.value.format(config_id=self.config_id))

    def delete(self) -> None:
        if (
            self.config_type == PricingImplementationTypes.discount.value
            and self.pricing_type == PricingTypes.volume.value
        ):
            self.db.query(DiscountGridTable).filter(
                DiscountGridTable.config_id == self.config_id
            ).delete()
            self._log()
        elif (
            self.config_type == PricingImplementationTypes.fee.value
            and self.pricing_type == PricingTypes.volume.value
        ):
            self.db.query(VolumeGridTable).filter(
                VolumeGridTable.config_id == self.config_id
            ).delete()
            self._log()
        elif (
            self.config_type == PricingImplementationTypes.fee.value
            and self.pricing_type == PricingTypes.peak.value
        ):
            self.db.query(PeakGridTable).filter(
                PeakGridTable.config_id == self.config_id
            ).delete()
            self._log()
        else:
            raise ConfigGridValidationError(
                pricing=self.pricing_type,
                config=self.config_type,
            )
