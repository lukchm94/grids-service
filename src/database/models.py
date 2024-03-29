from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, Sequence, String

from __app_configs import DbSequences, DbTables, Deliminator
from database.main import Base
from models.account import Account
from models.configs import BaseConfigResp
from models.grids import DiscountGrid, PeakOffPeakGrid, VolumeGrid
from models.volume import AcctVol


class ConfigTable(Base):
    __tablename__ = DbTables.configs.value

    id = Column(
        Integer, Sequence(DbSequences.config.value), primary_key=True, index=True
    )
    account_id = Column(Integer, ForeignKey(DbTables.account_fk.value))
    valid_from = Column(DateTime)
    valid_to = Column(DateTime)
    pricing_type = Column(String(55))
    config_type = Column(String(55))
    group = Column(String(55))
    package_size_option = Column(String(255))
    transport_option = Column(String(255))
    frequency = Column(String(55))
    deleted_at = Column(DateTime)

    def to_config(self) -> BaseConfigResp:
        package_size_option: str = self.package_size_option
        transport_option: str = self.transport_option

        return BaseConfigResp(
            account_id=self.account_id,
            valid_from=self.valid_from,
            valid_to=self.valid_to,
            pricing_type=self.pricing_type,
            config_type=self.config_type,
            group=self.group,
            package_size_option=package_size_option.split(Deliminator.comma.value),
            transport_option=transport_option.split(Deliminator.comma.value),
            frequency=self.frequency,
            deleted_at=self.deleted_at,
        )


class PeakGridTable(Base):
    __tablename__ = DbTables.peak_grids.value

    id = Column(
        Integer, Sequence(DbSequences.peak_grid.value), primary_key=True, index=True
    )
    config_id = Column(Integer, ForeignKey(DbTables.config_fk.value))
    min_volume_threshold = Column(Integer)
    max_volume_threshold = Column(Integer)
    min_distance_in_unit = Column(Float)
    max_distance_in_unit = Column(Float)
    weekday_option = Column(String(55))
    hour_start = Column(Integer)
    hour_end = Column(Integer)
    pickup_amount = Column(Integer)
    distance_amount_per_unit = Column(Integer)
    dropoff_amount = Column(Integer)

    def to_grid(self) -> PeakOffPeakGrid:
        weekday_option: str = self.weekday_option

        return PeakOffPeakGrid(
            min_volume_threshold=self.min_volume_threshold,
            max_volume_threshold=self.max_volume_threshold,
            min_distance_in_unit=self.min_distance_in_unit,
            max_distance_in_unit=self.max_distance_in_unit,
            weekday_option=[
                int(day) for day in weekday_option.split(Deliminator.comma.value)
            ],
            hour_start=self.hour_start,
            hour_end=self.hour_end,
            pickup_amount=self.pickup_amount,
            distance_amount_per_unit=self.distance_amount_per_unit,
            dropoff_amount=self.dropoff_amount,
        )


class VolumeGridTable(Base):
    __tablename__ = DbTables.volume_grids.value

    id = Column(
        Integer, Sequence(DbSequences.volume_grid.value), primary_key=True, index=True
    )
    config_id = Column(Integer, ForeignKey(DbTables.config_fk.value))
    min_volume_threshold = Column(Integer)
    max_volume_threshold = Column(Integer)
    min_distance_in_unit = Column(Float)
    max_distance_in_unit = Column(Float)
    pickup_amount = Column(Integer)
    distance_amount_per_unit = Column(Integer)
    dropoff_amount = Column(Integer)

    def to_grid(self) -> VolumeGrid:
        return VolumeGrid(
            min_volume_threshold=self.min_volume_threshold,
            max_volume_threshold=self.max_volume_threshold,
            min_distance_in_unit=self.min_distance_in_unit,
            max_distance_in_unit=self.max_distance_in_unit,
            pickup_amount=self.pickup_amount,
            distance_amount_per_unit=self.distance_amount_per_unit,
            dropoff_amount=self.dropoff_amount,
        )


class DiscountGridTable(Base):
    __tablename__ = DbTables.discount_grids.value

    id = Column(
        Integer, Sequence(DbSequences.discount_grid.value), primary_key=True, index=True
    )
    config_id = Column(Integer, ForeignKey(DbTables.config_fk.value))
    min_volume_threshold = Column(Integer)
    max_volume_threshold = Column(Integer)
    min_distance_in_unit = Column(Float)
    max_distance_in_unit = Column(Float)
    discount_amount = Column(Integer)

    def to_grid(self) -> DiscountGrid:
        return DiscountGrid(
            min_volume_threshold=self.min_volume_threshold,
            max_volume_threshold=self.max_volume_threshold,
            min_distance_in_unit=self.min_distance_in_unit,
            max_distance_in_unit=self.max_distance_in_unit,
            discount_amount=self.discount_amount,
        )


class AccountTable(Base):
    __tablename__ = DbTables.accounts.value

    id = Column(
        Integer, Sequence(DbSequences.account.value), primary_key=True, index=True
    )
    account_id = Column(Integer, ForeignKey(DbTables.account_fk.value))
    client_id = Column(Integer)
    client_group_name = Column(String(255))
    valid_from = Column(DateTime)
    valid_to = Column(DateTime)
    deleted_at = Column(DateTime)

    def to_account(self) -> Account:
        return Account(
            account_id=self.account_id,
            client_id=self.client_id,
            client_group_name=self.client_group_name,
            valid_from=self.valid_from,
            valid_to=self.valid_to,
            deleted_at=self.deleted_at,
        )


class AccountSequenceTable(Base):
    __tablename__ = DbTables.accounts_seq.value

    id = Column(
        Integer,
        Sequence(DbSequences.account_id.value),
        primary_key=True,
        index=True,
    )


class VolumesTable(Base):
    __tablename__ = DbTables.volumes.value

    id = Column(
        Integer,
        Sequence(DbSequences.volume.value),
        primary_key=True,
        index=True,
    )
    account_id = Column(Integer, ForeignKey(DbTables.account_fk.value))
    date = Column(DateTime)
    volume = Column(Integer)

    def to_acct_vol(self) -> AcctVol:
        return AcctVol(account_id=self.account_id, date=self.date, volume=self.volume)
