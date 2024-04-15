# database/main.py

from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

# Define the MySQL connection URL
DB_USER = "root"
DB_PASSWORD = "app_dev"
DB_HOST = "db"  # Service name of the MySQL container in Docker Compose
DB_PORT = "3306"
DB_NAME = "app_dev"
DB_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create the SQLAlchemy engine
engine = create_engine(DB_URL)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for declarative models
Base = declarative_base()


# Dependency to get the SQLAlchemy session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
