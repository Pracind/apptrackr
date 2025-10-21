import pytest
from fastapi.testclient import TestClient
from backend.main import app
import time

client = TestClient(app)

def signup_and_login():
    # Create a test user
    email = f"testuser{int(time.time())}@example.com"

    signup_resp = client.post("/signup", json={
        "email": email,
        "password": "password123",
        "name": "Test User"
    })
    assert signup_resp.status_code == 200

    # Log in
    login_resp = client.post("/login", json={
        "email": email,
        "password": "password123"
    })
    assert login_resp.status_code == 200
    return login_resp.json()["token"]

def test_create_and_get_app():
    token = signup_and_login()
    # Create application
    response = client.post("/apps", json={
        "company_name": "FakeCorp",
        "role_title": "Engineer",
        "city": "Paris",
        "country": "France",
        "applied_date": "2025-10-21T12:00:00"
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    app_data = response.json()
    app_id = app_data["id"]

    # Get application list
    response = client.get("/apps", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert any(app["id"] == app_id for app in response.json())

def test_update_and_delete_app():
    token = signup_and_login()
    # Create application
    response = client.post("/apps", json={
        "company_name": "FakeCorp",
        "role_title": "Engineer",
        "city": "Paris",
        "country": "France",
        "applied_date": "2025-10-21T12:00:00"
    }, headers={"Authorization": f"Bearer {token}"})
    app_id = response.json()["id"]

    # Update
    response = client.put(f"/apps/{app_id}", json={
        "status": "rejected"
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["status"] == "rejected"

    # Delete
    response = client.delete(f"/apps/{app_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["detail"] == "Application deleted"
