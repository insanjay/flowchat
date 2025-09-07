from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import os

# Database URL - SQLite file will be created in the root directory
SQLALCHEMY_DATABASE_URL = "sqlite:///./messaging_app.db"

# Create SQLAlchemy engine
# check_same_thread=False is needed for SQLite to work with FastAPI
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False  # Set to True for SQL query logging during development
)

# Create SessionLocal class - each instance will be a database session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Create Base class for our database models
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """
    Dependency function that provides database session to FastAPI endpoints
    Automatically handles session cleanup
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """
    Create all database tables
    Call this function when starting the app
    """
    from app.database.schemas import Base
    Base.metadata.create_all(bind=engine)

def drop_tables():
    """
    Drop all database tables
    Use with caution - only for development/testing
    """
    from app.database.schemas import Base
    Base.metadata.drop_all(bind=engine)
