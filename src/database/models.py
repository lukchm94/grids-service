from datetime import datetime, timedelta

from sqlalchemy import JSON, Column, DateTime, Float, Integer, Sequence, String

from database.main import Base


class Config(Base):
    __tablename__ = "configs"

    id = Column(Integer, Sequence("configs_id_seq"), primary_key=True, index=True)
    client_id = Column(Integer)
    valid_from = Column(DateTime, default=datetime.today() + timedelta(days=1))
    valid_to = Column(DateTime)
    pricing_type = Column(String(55))
    config_type = Column(String(55))
    package_size_option = Column(String(255))
    transport_option = Column(String(255))
    # TODO think about a better way to map grids as a FK
    grids_id = Column(String(55))


class PeakGridTable(Base):
    __tablename__ = "peak_grids"

    id = Column(Integer, Sequence("grids_id_seq"), primary_key=True, index=True)
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


class VolumeGridTable(Base):
    __tablename__ = "volume_grids"

    id = Column(Integer, Sequence("grids_id_seq"), primary_key=True, index=True)
    min_volume_threshold = Column(Integer)
    max_volume_threshold = Column(Integer)
    min_distance_in_unit = Column(Float)
    max_distance_in_unit = Column(Float)
    pickup_amount = Column(Integer)
    distance_amount_per_unit = Column(Integer)
    dropoff_amount = Column(Integer)


class DiscountGridTable(Base):
    __tablename__ = "discount_grids"

    id = Column(Integer, Sequence("grids_id_seq"), primary_key=True, index=True)
    min_volume_threshold = Column(Integer)
    max_volume_threshold = Column(Integer)
    min_distance_in_unit = Column(Float)
    max_distance_in_unit = Column(Float)
    dropoff_amount = Column(Integer)
