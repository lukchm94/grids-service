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
    empty = "Missing data for your query"
    group_ids = "group_ids"


class Env(str, ValidationEnum):
    dev = "dev"
    prod = "prod"


class Paths(str, Enum):
    root = "/"
    all = f"all{root}"
    last = f"last{root}"
    ind = f"{root}individual{root}"
    group = f"{root}group{root}"
    delete = "delete"
    config_tag = "configs"
    grids_tag = "grids"
    grids = f"{root}{grids_tag}"
    configs = f"{root}{config_tag}"
    volume = f"{root}volume"
    peak = f"{root}peak"
    discount = f"{root}discount"
    last_config = f"/{last}"
    all_config = f"/{all}"
    config_dates = f"/dates/"
    del_last_config = f"/{delete}/{last}"
    del_all_config = f"/{delete}/{all}"
    account_tag = "accounts"
    client_id = f"{root}client_id{root}"
    accounts = f"{root}{account_tag}"
    all_accounts = f"{root}{all}"
    all_acct_by_client = f"{client_id}{all}"
    last_account = f"{root}{last}"
    delete_account = f"{root}{delete}"


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


class Frequency(str, ValidationEnum):
    week = "weekly"
    month = "monthly"


class Groups(str, ValidationEnum):
    individual = "individual"
    group = "group"


class DbTables(str, ValidationEnum):
    configs = "configs"
    peak_grids = "peak_grids"
    volume_grids = "volume_grids"
    discount_grids = "discount_grids"
    accounts = "accounts"
    accounts_seq = "accounts_sequence"
    peak_table = "PeakGridTable"
    config_fk = f"{configs}.id"
    account_fk = f"{accounts_seq}.id"


class DbSequences(str, ValidationEnum):
    config = "configs_id_seq"
    peak_grid = "peak_grids_id_seq"
    volume_grid = "volume_grids_id_seq"
    discount_grid = "discount_grids_id_seq"
    account = "account_table_id_seq"
    account_id = "account_id_seq"


class BaseConfigFields(str, ValidationEnum):
    client_id = "client_id"
    valid_from = "valid_from"
    valid_to = "valid_to"
    pricing_type = "pricing_type"
    config_type = "config_type"
    package_size_option = "package_size_option"
    transport_option = "transport_option"
    freq = "frequency"
    group = "group"
    deleted_at = "deleted_at"


class ConfigField(str, ValidationEnum):
    grids = "grids"


class QueryFields(str, ValidationEnum):
    start = "start"
    end = "end"


class AccountFields(str, ValidationEnum):
    client_ids = "client_ids"
    valid_from = "valid_from"
    valid_to = "valid_to"
    deleted_at = "deleted_at"


class Defaults(ValidationEnum):
    """Default expiration for config is 2 years"""

    expiration: int = 366 + 365
    grid_amount: int = 100
    discount_amount: int = -50
    hour_start: int = 16
    hour_end: int = 23
    weekend_days_str: str = "4,5,6"
    weekend_days_list: list[int] = [4, 5, 6]
    client_ids_example: list[int] = [1001, 1002, 1003]
    group_name_example: str = "Test Client Group"
    ind_account_name: str = "Individual Account Client ID: {client_id}"
    account_id_seq: int = 1000000


class GridsValidationTypes(str, ValidationEnum):
    vol = "volume buckets"
    dist = "distance buckets"
    totals = "combined grids"


class LoggerConfig(str, ValidationEnum):
    log_name = "GridsService"
    default_level = "INFO"
    debug = "DEBUG"
    region_name = "eu-west-1"
    aws_group_name = "growth-service"
    aws_stream_name = "GridsService"


class LogMsg(str, ValidationEnum):
    config_updated = "Config: {config_id} for Account ID: {account_id} updated."
    config_created = "Config: {config_id} for Account ID: {account_id} created"
    config_deleted = "Config: {config_id} for Account ID: {account_id} deleted"
    config_expired = "Config: {config_id} for Account ID: {account_id} expired. ValidTo date changed to {expire_date}. ValidFrom data: {expire_from}"
    grids_created = (
        "Grids for Config: {config_id} for Account ID: {account_id} created."
    )
    grids_deleted = (
        "Grids for Config: {config_id} for Account ID: {account_id} deleted."
    )
    unsupported_config_grid = "Unsupported grid type: {grid} and config type: {config}"
    missing_grids = "No grids provided in request"
    missing_group = "No account Groups identified for the request"
    account_created = "Account ID: {account_id} for Client IDs: {client_ids} created."
    client_id_exists_in_account = "Client ID: {client_id} already mapped to the accounts: {account_ids}. Remove the client ID from the affected accounts first."
    client_id_in_account = "One of client IDs mapped to different account"
    account_deleted = "Account ID: {account_id} for Client IDs: {client_ids} created."
    account_not_found = "Account ID: {account_id} not found."
    no_account = "No account mapped to Client ID: {client_id}"
    account_exists = "Account ID: {account_id}. Exists for Client ID: {client_id}"
    acct_seq_created = "Account ID: {account_id} added to AccountSequenceTable"
