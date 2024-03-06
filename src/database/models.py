from datetime import datetime, timedelta

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, Sequence, String

from __app_configs import DbSequences, DbTables, Deliminator
from database.main import Base
from models.configs import BaseConfig
from models.grids import DiscountGrid, PeakOffPeakGrid, VolumeGrid


class ConfigTable(Base):
    __tablename__ = DbTables.configs.value

    id = Column(
        Integer, Sequence(DbSequences.config.value), primary_key=True, index=True
    )
    client_id = Column(Integer)
    valid_from = Column(DateTime, default=datetime.today() + timedelta(days=1))
    valid_to = Column(DateTime)
    pricing_type = Column(String(55))
    config_type = Column(String(55))
    package_size_option = Column(String(255))
    transport_option = Column(String(255))

    def to_config(self) -> BaseConfig:
        package_size_option: str = self.package_size_option
        transport_option: str = self.transport_option

        return BaseConfig(
            client_id=self.client_id,
            valid_from=self.valid_from,
            valid_to=self.valid_to,
            pricing_type=self.pricing_type,
            config_type=self.config_type,
            package_size_option=package_size_option.split(Deliminator.comma.value),
            transport_option=transport_option.split(Deliminator.comma.value),
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
        return PeakOffPeakGrid(
            min_volume_threshold=self.min_volume_threshold,
            max_volume_threshold=self.max_volume_threshold,
            min_distance_in_unit=self.min_distance_in_unit,
            max_distance_in_unit=self.max_distance_in_unit,
            weekday_option=self.weekday_option,
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
