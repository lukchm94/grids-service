from enum import Enum


def return_elements(elements: list) -> dict:
    if len(elements) == 0:
        return {AppVars.empty.value}
    return {AppVars.elements.value: len(elements), AppVars.data.value: elements}


class AppVars(str, Enum):
    elements = "elements"
    data = "data"
    hello = "Hello from root"
    empty = "Missing data for your query"


class Paths(str, Enum):
    root = "/"
    grids = f"{root}grids"
    configs = f"{root}configs"
    config_tag = "configs"
    grids_tag = "grids"


class GridsMergeCols(str, Enum):
    scheme_name = "scheme_name"
    brackets = "brackets"
    scheme_type = "scheme_type"
    config_type = "config_type"


class ClientCols(str, Enum):
    scheme = "scheme_name"
    id = "client_id"
    from_dt = "valid_from_date"
    to_dt = "valid_to_date"


class MergeTypes(str, Enum):
    left = "left"


class PriceToConvert(str, Enum):
    pu = "pickup_amount"
    distance = "distance_amount_per_unit"
    do = "dropoff_amount"

    @classmethod
    def list(cls) -> list[str]:
        return list(map(lambda c: c.value, cls))


class DiscountToConvert(str, Enum):
    discount_amount = "discount_amount"

    @classmethod
    def list(cls) -> list[str]:
        return list(map(lambda c: c.value, cls))


class PricingImplementationTypes(str, Enum):
    discount = "discount"
    fee = "fee"


class PricingTypes(str, Enum):
    volume = "volume"
    platform = "platform"
    peak = "peak_off_peak"


class PackageSizes(str, Enum):
    small = "SMALL"
    med = "MEDIUM"
    large = "LARGE"

    @classmethod
    def list(cls) -> list[str]:
        return list(map(lambda c: c.value, cls))


class TransportTypes(str, Enum):
    walk = "WALK"
    bike = "BIKE"
    car = "CAR"

    @classmethod
    def list(cls) -> list[str]:
        return list(map(lambda c: c.value, cls))
