from enum import Enum


def return_elements(elements: list) -> dict:
    if len(elements) == 0:
        return {AppVars.empty.value}
    return {AppVars.elements.value: len(elements), AppVars.data.value: elements}


class Deliminator(str, Enum):
    comma = ", "
    space = " "
    dash = "-"
    vertical = "|"
    forward_slash = "/"
    none = ""
    client_ref_field = " \\| "


class ValidationEnum(Enum):
    """ValidationEnum is a custom Parent class used in specific validations / configs inside the package."""

    @classmethod
    def list(cls) -> list:
        """Returns exact list of Enum values from the class"""
        return list(map(lambda c: c.value, cls))

    @classmethod
    def to_list(cls):
        """Converts the values and always returns a list of a single objects"""
        elements = []
        for id in cls:
            elements.extend(id.value)
        return elements

    @classmethod
    def to_string(cls, separator: str = Deliminator.comma.value):
        """
        Returns Enum values as a string separated by a separator.
        Separator defaults to Deliminator.comma.value
        """
        return separator.join([str(id) for id in cls.list()])

    @classmethod
    def to_dict(cls):
        """Returns Enums as a data dictionary {Enum.element.name: Enum.element.value}"""
        return {member.name: member.value for member in cls}


class AppVars(str, Enum):
    elements = "elements"
    data = "data"
    hello = "Hello from root"
    empty = "Missing data for your query"
    no_client_config = "No Config identified for Client ID: {client_id}"


class Paths(str, Enum):
    root = "/"
    all = "all"
    last = "last"
    grids = f"{root}grids"
    configs = f"{root}configs"
    config_tag = "configs"
    grids_tag = "grids"
    volume = f"{root}volume"
    peak = f"{root}peak"
    discount = f"{root}discount"
    create = "create"
    create_vol = f"/{create}/volume/"
    create_peak = f"/{create}/peak/"
    create_disc = f"/{create}/discount/"
    last_config = f"{configs}{grids}/{last}/"
    all_config = f"{configs}{grids}/{all}/"


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


class PriceToConvert(str, ValidationEnum):
    pu = "pickup_amount"
    distance = "distance_amount_per_unit"
    do = "dropoff_amount"


class DiscountToConvert(str, ValidationEnum):
    discount_amount = "discount_amount"


class PricingImplementationTypes(str, ValidationEnum):
    discount = "discount"
    fee = "fee"


class PricingTypes(str, ValidationEnum):
    volume = "volume"
    platform = "platform"
    peak = "peak_off_peak"


class PackageSizes(str, ValidationEnum):
    small = "SMALL"
    med = "MEDIUM"
    large = "LARGE"


class TransportTypes(str, ValidationEnum):
    walk = "WALK"
    bike = "BIKE"
    car = "CAR"


class DbTables(str, ValidationEnum):
    configs = "configs"
    peak_grids = "peak_grids"
    volume_grids = "volume_grids"
    discount_grids = "discount_grids"
    config_table = "ConfigTable"
    discount_table = "DiscountGridTable"
    volume_table = "VolumeGridTable"
    peak_table = "PeakGridTable"
    config_fk = f"{configs}.id"


class DbSequences(str, ValidationEnum):
    config = "configs_id_seq"
    peak_grid = "peak_grids_id_seq"
    volume_grid = "volume_grids_id_seq"
    discount_grid = "discount_grids_id_seq"


class BaseConfigFields(str, ValidationEnum):
    client_id = "client_id"
    valid_from = "valid_from"
    valid_to = "valid_to"
    pricing_type = "pricing_type"
    config_type = "config_type"
    package_size_option = "package_size_option"
    transport_option = "transport_option"


class Defaults(ValidationEnum):
    """Default expiration for config is 2 years"""

    expiration: int = 366 + 365
    grid_amount: int = 100
    discount_amount: int = -50
    hour_start: int = 16
    hour_end: int = 23
    weekend_days_str: str = "4,5,6"
    weekend_days_list: list[int] = [4, 5, 6]


class GridsValidationTypes(str, ValidationEnum):
    vol = "volume buckets"
    dist = "distance buckets"
    totals = "combined grids"
