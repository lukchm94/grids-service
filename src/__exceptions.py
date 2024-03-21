from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import HTTPException


# TODO add the HTTPExceptions to the regular Exceptions
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


class DatesError(HTTPException):
    def __init__(
        self,
        valid_from: datetime,
        valid_to: datetime,
        status_code: int = 422,
        detail: str = "Invalid dates; DateStart: {valid_from} smaller than DateEnd: {valid_to}",
        headers: Dict[str, str] | None = None,
    ) -> None:
        super().__init__(status_code, detail, headers)
        self.detail = self.detail.format(valid_to=valid_to, valid_from=valid_from)


class InvalidConfigError(Exception):
    def __init__(
        self,
        config: Optional[str] = None,
        pricing: Optional[str] = None,
    ) -> None:
        super().__init__(
            f"Invalid configuration received. Configuration: {config}, Pricing Type: {pricing}."
        )


class InvalidGroupError(HTTPException):
    def __init__(
        self,
        group: Optional[str] = None,
        status_code: int = 422,
        detail: str = "Received unsupported FeeType: {group}",
        headers: Dict[str, str] | None = None,
    ) -> None:
        super().__init__(status_code, detail, headers)
        self.detail = self.detail.format(group=group)


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
        db_id: str,
        req_id: str,
        status_code: int = 422,
        detail: Any = "Two Client IDs not identical. ID in DB: {db_id}, Requested ID: {req_id}",
        headers: Dict[str, str] | None = None,
    ) -> None:
        super().__init__(status_code, detail, headers)
        self.detail = self.detail.format(db_id=db_id, req_id=req_id)


class UnsupportedConfigAfterUpdateError(HTTPException):
    def __init__(
        self,
        grid: str,
        config: str,
        status_code: int = 422,
        detail: Any = "Unsupported grid type: {grid} and config type: {config}",
        headers: Dict[str, str] | None = None,
    ) -> None:
        super().__init__(status_code, detail, headers)
        self.detail = self.detail.format(grid=grid, config=config)


class ConfigGridValidationError(HTTPException):
    def __init__(
        self,
        pricing: str = None,
        config: str = None,
        status_code: int = 404,
        detail: str = "Invalid pricing type: {pricing} and config type: {config} provided",
        headers: Dict[str, str] | None = None,
    ) -> None:
        super().__init__(status_code, detail, headers)
        self.detail = self.detail.format(pricing=pricing, config=config)


class GridsValuesError(HTTPException):
    def __init__(
        self,
        client_id: int,
        type: str,
        status_code: int = 422,
        detail: str = "{client_id} - Invalid grids values after ordering. {type} check",
        headers: Dict[str, str] | None = None,
    ) -> None:
        super().__init__(status_code, detail, headers)
        self.detail = self.detail.format(client_id=client_id, type=type.upper())
