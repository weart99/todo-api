import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.todo_api.main import app
from src.todo_api.database import get_db
from src.todo_api.models import Base

TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    # Create the database tables for testing
    Base.metadata.create_all(bind=engine)

    # Override the get_db dependency to use the test database
    app.dependency_overrides[get_db] = override_get_db

    # Create a TestClient instance
    with TestClient(app) as test_client:
        yield test_client

    # Drop the database tables after tests
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()
