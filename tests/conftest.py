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


@pytest.fixture
def test_user_data(client):
    """Test user data for authentication."""
    return {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword123",
    }


@pytest.fixture
def created_user(client, test_user_data):
    """Create a user with API"""
    response = client.post("/auth/register", json=test_user_data)
    return response.json()


@pytest.fixture
def auth_token(client, test_user_data, created_user):
    """Valid authentication token"""
    # Log in to get the token
    login_data = {
        "username": test_user_data["username"],
        "password": test_user_data["password"],
    }
    response = client.post("/auth/login", json=login_data)
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(auth_token):
    """Headers with authentication token"""
    return {"Authorization": f"Bearer {auth_token}"}
