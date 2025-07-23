import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./todo.db")

if DATABASE_URL.startswith("sqlite:///"):
    # For SQLite, we need to set check_same_thread=False
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    # For other databases, we can use the default connection arguments
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
