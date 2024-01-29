import pytest

from __configs import PackageSizes
from models.grids import DiscountGrid, PeakOffPeakGrid, VolumeGrid


# @pytest.fixture
def volume_grid_1() -> VolumeGrid:
    return VolumeGrid(
        min_volume_threshold=1,
        max_volume_threshold=10,
        min_distance_in_unit=0,
        max_distance_in_unit=2.5,
        package_size_option=PackageSizes.list(),
        pickup_amount=100,
        distance_amount_per_unit=50,
        dropoff_amount=100,
    )


# @pytest.fixture
def volume_grid_2() -> VolumeGrid:
    return VolumeGrid(
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
        min_volume_threshold=10,
        max_volume_threshold=None,
        min_distance_in_unit=2.5,
        max_distance_in_unit=None,
        pickup_amount=50,
        distance_amount_per_unit=100,
        dropoff_amount=75,
    )
