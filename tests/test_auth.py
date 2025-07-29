def test_register_user(client, test_user_data):
    """Test user registration."""
    response = client.post("/auth/register", json=test_user_data)
    assert response.status_code == 200

    data = response.json()
    assert data["username"] == test_user_data["username"]
    assert data["email"] == test_user_data["email"]
    assert data["is_active"] is True
    assert "hashed_password" not in data  # Ensure password is not returned
    assert "password" not in data  # Ensure password is not returned
    assert "id" in data


def test_register_user_existing_username(client, test_user_data):
    """Test registration with an existing username."""
    client.post("/auth/register", json=test_user_data)  # Register first user
    response = client.post(
        "/auth/register", json=test_user_data
    )  # Try to register again
    assert response.status_code == 400
    assert response.json() == {"detail": "Username already exists"}


def test_register_user_existing_email(client, test_user_data):
    """Test registration with an existing email."""
    client.post("/auth/register", json=test_user_data)  # Register first user
    new_user_data = test_user_data.copy()
    new_user_data["username"] = "newuser"  # Change username to avoid conflict
    response = client.post(
        "/auth/register", json=new_user_data
    )  # Try to register again
    assert response.status_code == 400
    assert response.json() == {"detail": "Email already registered"}


def test_login_user(client, test_user_data):
    """Test user login."""
    client.post("/auth/register", json=test_user_data)  # Register first user
    # Prepare login data
    login_data = {
        "username": test_user_data["username"],
        "password": test_user_data["password"],
    }
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert isinstance(data["access_token"], str)


def test_login_wrong_password(client, test_user_data):
    """Test login with wrong password."""
    client.post("/auth/register", json=test_user_data)  # Register first user
    wrong_login_data = {
        "username": test_user_data["username"],
        "password": "wrongpassword",
    }
    response = client.post("/auth/login", json=wrong_login_data)
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect password"}


def test_login_nonexistent_user(client):
    """Test login with a non-existent user."""
    login_data = {"username": "nonexistentuser", "password": "somepassword"}
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 404
    assert response.json() == {"detail": "Username not found"}


def test_get_current_user_info(client, auth_headers, test_user_data):
    """Test /me endpoint with valid token."""
    response = client.get("/auth/me", headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert data["username"] == test_user_data["username"]
    assert data["email"] == test_user_data["email"]
    assert data["is_active"] is True
    assert "hashed_password" not in data  # Ensure password is not returned
    assert "password" not in data  # Ensure password is not returned
    assert "id" in data


def test_get_tasks_requires_auth(client):
    """Test that tasks endpoint requires authentication."""
    response = client.get("/tasks/")
    assert response.status_code == 403
    assert "detail"


def test_create_task_with_auth(client, auth_headers):
    """Test creating a task with authentication."""
    task_data = {
        "title": "Authenticated Task",
        "description": "This task requires auth",
    }
    response = client.post("/tasks/", json=task_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == task_data["title"]
    assert data["description"] == task_data["description"]
    assert data["status"] == "To do"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_user_isolation(client):
    """Test that users can only see their own tasks."""

    # Create first user
    user1_data = {
        "username": "user1",
        "email": "user1@example.com",
        "password": "password123",
    }
    client.post("/auth/register", json=user1_data)

    # Connect as user1 to get token
    login1_response = client.post(
        "/auth/login",
        json={"username": user1_data["username"], "password": user1_data["password"]},
    )
    user1_token = login1_response.json()["access_token"]
    user1_headers = {"Authorization": f"Bearer {user1_token}"}

    # Create a task for user1
    task1_data = {"title": "Task by User 1", "description": "Private task"}
    response1 = client.post("/tasks/", json=task1_data, headers=user1_headers)
    user1_task_id = response1.json()["id"]

    # Create second user
    user2_data = {
        "username": "user2",
        "email": "user2@example.com",
        "password": "password456",
    }
    client.post("/auth/register", json=user2_data)

    # Connect as user2 to get token
    login2_response = client.post(
        "/auth/login",
        json={"username": user2_data["username"], "password": user2_data["password"]},
    )
    user2_token = login2_response.json()["access_token"]
    user2_headers = {"Authorization": f"Bearer {user2_token}"}

    # Create a task for user2
    task2_data = {"title": "Task by User 2", "description": "Another private task"}
    response2 = client.post("/tasks/", json=task2_data, headers=user2_headers)
    user2_task_id = response2.json()["id"]

    # User1 can see their own task
    user1_tasks = client.get("/tasks/", headers=user1_headers).json()
    assert len(user1_tasks) == 1
    assert user1_tasks[0]["id"] == user1_task_id
    assert user1_tasks[0]["title"] == "Task by User 1"

    # User2 can see their own task
    user2_tasks = client.get("/tasks/", headers=user2_headers).json()
    assert len(user2_tasks) == 1
    assert user2_tasks[0]["id"] == user2_task_id
    assert user2_tasks[0]["title"] == "Task by User 2"

    # User1 cannot see User2's task
    response = client.get(f"/tasks/{user2_task_id}", headers=user1_headers)
    assert response.status_code == 404  # Task not found (car pas la sienne)
