from datetime import datetime
from logging import Logger

from fastapi import HTTPException

from __app_configs import LogMsg
from __exceptions import AccountNotFoundError, VolumesNotFoundError
from database.main import db_dependency
from database.models import VolumesTable
from models.query_req import DatesReq
from models.volume import AcctVolResp


class Getter:
    logger: Logger
    db: db_dependency

    def __init__(self, logger: Logger, db: db_dependency) -> None:
        self.logger = logger
        self.db = db

    def _get_total_vol(self, volumes: list[VolumesTable]) -> int:
        return sum([vol.to_acct_vol().volume for vol in volumes])

    def _get_start_date(self, volumes: list[VolumesTable]) -> datetime:
        return min([vol.to_acct_vol().date for vol in volumes])

    def _get_end_date(self, volumes: list[VolumesTable]) -> datetime:
        return max([vol.to_acct_vol().date for vol in volumes])

    def volumes_from_dates(self, id: int, dates_req: DatesReq) -> AcctVolResp:
        daily_volumes = (
            self.db.query(VolumesTable)
            .filter(VolumesTable.account_id == id)
            .filter(VolumesTable.date >= dates_req.start)
            .filter(VolumesTable.date < dates_req.end)
            .all()
        )
        if len(daily_volumes) == 0:
            raise VolumesNotFoundError(id, dates_req.to_str())

        return AcctVolResp(
            account_id=id,
            total_vol=self._get_total_vol(daily_volumes),
            date_start=self._get_start_date(daily_volumes),
            date_end=self._get_end_date(daily_volumes),
        )


class Setter:
    logger: Logger
    db: db_dependency

    def __init__(self, logger: Logger, db: db_dependency) -> None:
        self.logger = logger
        self.db = db
