from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Union

from models.query_req import DatesReq


@dataclass
class DateReqController:
    start: Union[None, datetime]
    end: Union[None, datetime]

    def __post_init__(self) -> None:
        if self.start is None:
            self.start = datetime.now()
        if self.end is None:
            self.end = datetime.now() + timedelta(days=1)

    def format(self) -> DatesReq:
        return DatesReq(start=self.start, end=self.end)
