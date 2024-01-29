from __future__ import annotations

from datetime import datetime

import pytest

from __configs import (
    PackageSizes,
    PricingImplementationTypes,
    PricingTypes,
    TransportTypes,
)
from __fixtures.grids import volume_grid_1, volume_grid_2, volume_grid_3, volume_grid_4
from models.configs import Config
from models.grids import DiscountGrid, PeakOffPeakGrid, VolumeGrid


# @pytest.fixture
def config_with_volume_grid() -> Config:
    return Config(
        client_id=123,
        valid_from=datetime(2024, 1, 1),
        valid_to=None,
        pricing_type=PricingTypes.volume.value,
        config_type=PricingImplementationTypes.fee.value,
        package_size_option=PackageSizes.list(),
        transport_option=TransportTypes.list(),
        grids=[volume_grid_1(), volume_grid_2(), volume_grid_3(), volume_grid_4()],
    )
