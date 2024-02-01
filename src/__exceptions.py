from datetime import datetime
from typing import Any, Optional


class DatesError(Exception):
    def __init__(self, valid_from: datetime, valid_to: datetime) -> None:
        super().__init__(
            f"Invalid configs: {str(valid_from.date())} smaller than {str(valid_to.date())}"
        )


class InvalidDayError(Exception):
    def __init__(self, day: int) -> None:
        super().__init__(f"Invalid day: {day}. Day must be between 0 and 6")


class HoursError(Exception):
    def __init__(self) -> None:
        super().__init__("Hours configuration invalid")


class InvalidInputError(Exception):
    def __init__(self, value: Any) -> None:
        super().__init__(
            f"Received {value} of type: {type(value)} not allowed for the field"
        )


class InvalidConfigError(Exception):
    def __init__(
        self,
        config: Optional[str] = None,
        pricing: Optional[str] = None,
    ) -> None:
        super().__init__(
            f"Invalid configuration received. Configuration: {config}, Pricing Type: {pricing}."
        )


class UnsupportedFeeTypeError(Exception):
    def __init__(self, fee_type: str) -> None:
        super().__init__(f"Received unsupported FeeType: {fee_type}")


class UnsupportedPriceTypeError(Exception):
    def __init__(self, type: str) -> None:
        super().__init__(f"Received unsupported PriceType: {type}")


class UnsupportedConfigError(Exception):
    def __init__(self, grid_type: str, config_type: str) -> None:
        super().__init__(
            f"Unsupported grid type: {grid_type} or config type: {config_type}"
        )
