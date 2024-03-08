from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import HTTPException


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


class GridReqConversionError(ValueError):
    def __init__(self) -> None:
        super().__init__(
            "Each item in 'grids' must be an instance of VolumeGrid, PeakOffPeakGrid, or DiscountGrid"
        )


class ClientIdConfigError(HTTPException):
    def __init__(
        self,
        status_code: int = 422,
        detail: Any = f"Two Client IDs not identical",
        headers: Dict[str, str] | None = None,
    ) -> None:
        super().__init__(status_code, detail, headers)


class UnsupportedConfigAfterUpdateError(HTTPException):
    def __init__(
        self,
        status_code: int = 422,
        detail: Any = "Unsupported grid type and config type",
        headers: Dict[str, str] | None = None,
    ) -> None:
        super().__init__(status_code, detail, headers)


class ConfigGridValidationError(HTTPException):
    def __init__(
        self,
        status_code: int = 404,
        detail: Any = "Invalid pricing type and config type provided",
        headers: Dict[str, str] | None = None,
    ) -> None:
        super().__init__(status_code, detail, headers)
