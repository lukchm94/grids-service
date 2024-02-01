from __future__ import annotations

from datetime import datetime

import pytest

from __app_configs import (
    PackageSizes,
    PricingImplementationTypes,
    PricingTypes,
    TransportTypes,
)
from __fixtures.grids import discount_grids, peak_grids, vol_grids
from models.configs import Config


# @pytest.fixture
def config_with_volume_grid() -> Config:
    return Config(
        id=1,
        client_id=123,
        valid_from=datetime(2024, 1, 1),
        valid_to=None,
        pricing_type=PricingTypes.volume.value,
        config_type=PricingImplementationTypes.fee.value,
        package_size_option=PackageSizes.list(),
        transport_option=TransportTypes.list(),
        grids=vol_grids(),
    )


# @pytest.fixture
def config_with_peak_grid() -> Config:
    return Config(
        id=2,
        client_id=234,
        valid_from=datetime(2024, 1, 1),
        valid_to=None,
        pricing_type=PricingTypes.peak.value,
        config_type=PricingImplementationTypes.fee.value,
        package_size_option=PackageSizes.list(),
        transport_option=TransportTypes.list(),
        grids=peak_grids(),
    )


# @pytest.fixture
def config_with_discount_grid() -> Config:
    return Config(
        id=3,
        client_id=345,
        valid_from=datetime(2024, 1, 1),
        valid_to=None,
        pricing_type=PricingTypes.volume.value,
        config_type=PricingImplementationTypes.discount.value,
        package_size_option=PackageSizes.list(),
        transport_option=TransportTypes.list(),
        grids=discount_grids(),
    )


def get_all_configs() -> list[Config]:
    return [
        config_with_discount_grid(),
        config_with_peak_grid(),
        config_with_volume_grid(),
    ]
