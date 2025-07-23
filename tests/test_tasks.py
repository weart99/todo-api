def test_create_task(client):
    response = client.post(
        "/tasks/",
        json={
            "title": "Test Task",
            "description": "This is a test task",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["description"] == "This is a test task"
    assert data["status"] == "To do"
    assert isinstance(data["id"], int)
    assert "created_at" in data
    assert "updated_at" in data


def test_get_tasks_empty(client):
    response = client.get("/tasks/")
    assert response.status_code == 200
    assert response.json() == []


def test_get_tasks_not_found(client):
    response = client.get("/tasks/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}


def test_create_and_get_task(client):
    create_response = client.post(
        "/tasks/",
        json={
            "title": "New Task",
            "description": "This is a new task",
        },
    )
    assert create_response.status_code == 200
    task_id = create_response.json()["id"]

    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["title"] == "New Task"
    assert data["description"] == "This is a new task"
    assert data["status"] == "To do"
    assert data["id"] == task_id


def test_update_task(client):
    create_response = client.post(
        "/tasks/",
        json={
            "title": "Task to Update",
            "description": "This task will be updated",
        },
    )
    assert create_response.status_code == 200
    task_id = create_response.json()["id"]

    update_response = client.put(
        f"/tasks/{task_id}",
        json={
            "title": "Updated Task",
            "description": "This task has been updated",
            "status": "Doing",
        },
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["title"] == "Updated Task"
    assert data["description"] == "This task has been updated"
    assert data["status"] == "Doing"


def test_delete_task(client):
    create_response = client.post(
        "/tasks/",
        json={
            "title": "Task to Delete",
            "description": "This task will be deleted",
        },
    )
    assert create_response.status_code == 200
    task_id = create_response.json()["id"]

    delete_response = client.delete(f"/tasks/{task_id}")
    assert delete_response.status_code == 200
    assert delete_response.json() == {"detail": "Task deleted successfully"}

    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 404
    assert get_response.json() == {"detail": "Task not found"}


def test_update_partial_task(client):
    create_response = client.post(
        "/tasks/",
        json={
            "title": "Partial Update Task",
            "description": "This task will be partially updated",
        },
    )
    assert create_response.status_code == 200
    task_id = create_response.json()["id"]

    update_response = client.put(
        f"/tasks/{task_id}",
        json={
            "title": "Partially Updated Task",
        },
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["title"] == "Partially Updated Task"
    assert data["description"] == "This task will be partially updated"
    assert data["status"] == "To do"


def test_update_nonexistent_task(client):
    response = client.put(
        "/tasks/999",
        json={
            "title": "Nonexistent Task",
        },
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}


def test_delete_nonexistent_task(client):
    response = client.delete("/tasks/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}
