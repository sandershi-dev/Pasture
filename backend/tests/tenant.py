# tests/test_tenants.py
# Pytest tests for Tenant MVC

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# Sample tenant payload
sample_tenant = {
    "full_name": "Alice Tenant",
    "email": "alice@example.com",
    "phone": "5551234567",
    "date_of_birth": "1990-05-20",
    "government_id": "ABC123456",
    "emergency_contact": {"name": "Bob", "phone": "5559998888"}
}

updated_tenant = {
    "full_name": "Alice Updated",
    "email": "alice.new@example.com",
    "phone": "5557776666",
    "date_of_birth": "1991-06-21",
    "government_id": "XYZ987654",
    "emergency_contact": {"name": "Charlie", "phone": "5551112222"}
}

# -----------------------------
# CREATE TENANT
# -----------------------------
def test_create_tenant():
    response = client.post("/tenants/", json=sample_tenant)
    assert response.status_code == 201
    data = response.json()
    assert data["full_name"] == "Alice Tenant"
    assert "id" in data

# -----------------------------
# GET ALL TENANTS
# -----------------------------
def test_get_tenants():
    response = client.get("/tenants/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# -----------------------------
# GET TENANT BY ID
# -----------------------------
def test_get_tenant_by_id():
    create = client.post("/tenants/", json=sample_tenant)
    tenant_id = create.json()["id"]

    response = client.get(f"/tenants/{tenant_id}")
    assert response.status_code == 200
    assert response.json()["id"] == tenant_id

# -----------------------------
# UPDATE TENANT
# -----------------------------
def test_update_tenant():
    create = client.post("/tenants/", json=sample_tenant)
    tenant_id = create.json()["id"]

    response = client.put(f"/tenants/{tenant_id}", json=updated_tenant)
    assert response.status_code == 200

    data = response.json()
    assert data["full_name"] == "Alice Updated"
    assert data["email"] == "alice.new@example.com"
    assert data["government_id"] == "XYZ987654"

# -----------------------------
# DELETE TENANT
# -----------------------------
def test_delete_tenant():
    create = client.post("/tenants/", json=sample_tenant)
    tenant_id = create.json()["id"]

    response = client.delete(f"/tenants/{tenant_id}")
    assert response.status_code == 204

    # Ensure tenant is gone
    check = client.get(f"/tenants/{tenant_id}")
    assert check.status_code == 404
