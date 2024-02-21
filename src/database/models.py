from datetime import datetime, timedelta

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, Sequence, String
from sqlalchemy.orm import relationship

from __app_configs import DbSequences, DbTables
from database.main import Base


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
    discount_grids = relationship(
        DbTables.discount_table.value, back_populates=DbTables.configs.value
    )
    peak_grids = relationship(
        DbTables.peak_table.value, back_populates=DbTables.configs.value
    )
    volume_grids = relationship(
        DbTables.volume_table.value, back_populates=DbTables.configs.value
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
    config = relationship(
        DbTables.config_table.value, back_populates=DbTables.peak_grids.value
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
    config = relationship(
        DbTables.config_table.value, back_populates=DbTables.volume_grids.value
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
    dropoff_amount = Column(Integer)
    config = relationship(
        DbTables.config_table.value, back_populates=DbTables.discount_grids.value
    )
