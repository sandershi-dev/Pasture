# tests/test_users.py
# Pytest-based tests for User MVC (FastAPI)

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# Sample payloads
sample_user = {
    "full_name": "John Doe",
    "email": "john@example.com",
    "password": "Password123!",
    "role": "staff",
    "phone": "1234567890"
}

updated_user = {
    "full_name": "John Updated",
    "email": "john_updated@example.com",
    "role": "manager",
    "phone": "9876543210"
}

# -----------------------------
# CREATE USER
# -----------------------------
def test_create_user():
    response = client.post("/users/", json=sample_user)
    assert response.status_code == 201
    data = response.json()
    assert data["full_name"] == "John Doe"
    assert "id" in data

# -----------------------------
# GET ALL USERS
# -----------------------------
def test_get_users():
    response = client.get("/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# -----------------------------
# GET USER BY ID
# -----------------------------
def test_get_user_by_id():
    create = client.post("/users/", json=sample_user)
    user_id = create.json()["id"]

    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["id"] == user_id

# -----------------------------
# UPDATE USER
# -----------------------------
def test_update_user():
    create = client.post("/users/", json=sample_user)
    user_id = create.json()["id"]

    response = client.put(f"/users/{user_id}", json=updated_user)
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "John Updated"
    assert data["email"] == "john_updated@example.com"
    assert data["role"] == "manager"

# -----------------------------
# DELETE USER
# -----------------------------
def test_delete_user():
    create = client.post("/users/", json=sample_user)
    user_id = create.json()["id"]

    response = client.delete(f"/users/{user_id}")
    assert response.status_code == 204

    # Ensure user is removed
    check = client.get(f"/users/{user_id}")
    assert check.status_code == 404
