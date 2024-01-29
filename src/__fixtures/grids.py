from xml.dom.domreg import well_known_implementations

import pytest

from models.grids import DiscountGrid, Grid, PeakOffPeakGrid, VolumeGrid


# @pytest.fixture
def volume_grid_1() -> VolumeGrid:
    return VolumeGrid(
        id=1,
        min_volume_threshold=1,
        max_volume_threshold=10,
        min_distance_in_unit=0,
        max_distance_in_unit=2.5,
        pickup_amount=100,
        distance_amount_per_unit=50,
        dropoff_amount=100,
    )


# @pytest.fixture
def volume_grid_2() -> VolumeGrid:
    return VolumeGrid(
        id=2,
        min_volume_threshold=10,
        max_volume_threshold=None,
        min_distance_in_unit=0,
        max_distance_in_unit=2.5,
        pickup_amount=100,
        distance_amount_per_unit=50,
        dropoff_amount=75,
    )


# @pytest.fixture
def volume_grid_3() -> VolumeGrid:
    return VolumeGrid(
        id=3,
        min_volume_threshold=1,
        max_volume_threshold=10,
        min_distance_in_unit=2.5,
        max_distance_in_unit=None,
        pickup_amount=50,
        distance_amount_per_unit=100,
        dropoff_amount=100,
    )


# @pytest.fixture
def volume_grid_4() -> VolumeGrid:
    return VolumeGrid(
        id=4,
        min_volume_threshold=10,
        max_volume_threshold=None,
        min_distance_in_unit=2.5,
        max_distance_in_unit=None,
        pickup_amount=50,
        distance_amount_per_unit=100,
        dropoff_amount=75,
    )


# @pytest.fixture
def peak_grid_1() -> PeakOffPeakGrid:
    return PeakOffPeakGrid(
        id=5,
        min_volume_threshold=1,
        max_volume_threshold=10,
        min_distance_in_unit=0,
        max_distance_in_unit=2.5,
        pickup_amount=100,
        distance_amount_per_unit=50,
        dropoff_amount=200,
        weekday_option=[4, 5, 6],
        hour_start=18,
        hour_end=23,
    )


# @pytest.fixture
def peak_grid_2() -> PeakOffPeakGrid:
    return PeakOffPeakGrid(
        id=6,
        min_volume_threshold=10,
        max_volume_threshold=None,
        min_distance_in_unit=0,
        max_distance_in_unit=2.5,
        pickup_amount=100,
        distance_amount_per_unit=50,
        dropoff_amount=150,
        weekday_option=[4, 5, 6],
        hour_start=18,
        hour_end=23,
    )


# @pytest.fixture
def peak_grid_3() -> PeakOffPeakGrid:
    return PeakOffPeakGrid(
        id=7,
        min_volume_threshold=1,
        max_volume_threshold=10,
        min_distance_in_unit=2.5,
        max_distance_in_unit=None,
        pickup_amount=100,
        distance_amount_per_unit=100,
        dropoff_amount=100,
        weekday_option=[4, 5, 6],
        hour_start=18,
        hour_end=23,
    )


# @pytest.fixture
def peak_grid_4() -> PeakOffPeakGrid:
    return PeakOffPeakGrid(
        id=8,
        min_volume_threshold=10,
        max_volume_threshold=None,
        min_distance_in_unit=2.5,
        max_distance_in_unit=None,
        pickup_amount=100,
        distance_amount_per_unit=100,
        dropoff_amount=75,
        weekday_option=[4, 5, 6],
        hour_start=18,
        hour_end=23,
    )


# @pytest.fixture
def discount_grid_1() -> DiscountGrid:
    return DiscountGrid(
        id=9,
        min_volume_threshold=1,
        max_volume_threshold=10,
        min_distance_in_unit=0,
        max_distance_in_unit=2.5,
        discount_amount=-50,
    )


# @pytest.fixture
def discount_grid_2() -> DiscountGrid:
    return DiscountGrid(
        id=10,
        min_volume_threshold=10,
        max_volume_threshold=None,
        min_distance_in_unit=0,
        max_distance_in_unit=2.5,
        discount_amount=-60,
    )


# @pytest.fixture
def discount_grid_3() -> DiscountGrid:
    return DiscountGrid(
        id=11,
        min_volume_threshold=1,
        max_volume_threshold=10,
        min_distance_in_unit=2.5,
        max_distance_in_unit=None,
        discount_amount=-80,
    )


# @pytest.fixture
def discount_grid_4() -> DiscountGrid:
    return DiscountGrid(
        id=12,
        min_volume_threshold=10,
        max_volume_threshold=None,
        min_distance_in_unit=2.5,
        max_distance_in_unit=None,
        discount_amount=-100,
    )


def vol_grids() -> list[VolumeGrid]:
    return [volume_grid_1(), volume_grid_2(), volume_grid_3(), volume_grid_4()]


def peak_grids() -> list[PeakOffPeakGrid]:
    return [peak_grid_1(), peak_grid_2(), peak_grid_3(), peak_grid_4()]


def discount_grids() -> list[DiscountGrid]:
    return [
        discount_grid_1(),
        discount_grid_2(),
        discount_grid_3(),
        discount_grid_4(),
    ]


def get_all_grids() -> list[Grid]:
    return [
        volume_grid_1(),
        volume_grid_2(),
        volume_grid_3(),
        volume_grid_4(),
        peak_grid_1(),
        peak_grid_2(),
        peak_grid_3(),
        peak_grid_4(),
        discount_grid_1(),
        discount_grid_2(),
        discount_grid_3(),
        discount_grid_4(),
    ]
