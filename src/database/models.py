from ast import Str
from datetime import datetime, timedelta

from sqlalchemy import Column, Date, Float, ForeignKey, Integer, Sequence, String, null

from database.main import Base


class Config(Base):
    __tablename__ = "configs"

    id = Column(Integer, Sequence("configs_id_seq"), primary_key=True, index=True)
    valid_from = Column(Date, default=datetime.today().date() + timedelta(days=1))
    valid_to = Column(Date, nullable=True)
    pricing_type = Column(String)
    config_type = Column(String)
    package_size_option = Column(String)
    transport_option = Column(String)
    grids_id = Column(Integer, ForeignKey("grids.id"))


class Grid(Base):
    __tablename__ = "grids"

    id = Column(Integer, Sequence("grids_id_seq"), primary_key=True, index=True)
    min_volume_threshold = Column(Integer)
    max_volume_threshold = Column(Integer)
    min_distance_in_unit = Column(Float)
    max_distance_in_unit = Column(Float)
    weekday_option = Column(String, nullable=True, default=None)
    hour_start = Column(Integer, nullable=True, default=None)
    hour_end = Column(Integer, nullable=True, default=None)
    pickup_amount = Column(Integer, nullable=True, default=None)
    distance_amount_per_unit = Column(Integer, nullable=True, default=None)
    dropoff_amount = Column(Integer, nullable=True, default=None)
    discount_amount = Column(Integer, nullable=True, default=None)
