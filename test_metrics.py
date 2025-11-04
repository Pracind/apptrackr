# test_metrics.py

import pytest
import uuid
from fastapi.testclient import TestClient
from backend.main import app, engine, pwd_context  # ensure your pwd_context uses bcrypt as in your backend
from sqlmodel import Session, delete
from backend.models import User, Application
from datetime import datetime
import pandas as pd

client = TestClient(app)

ACTUAL_PASSWORD = "testing123"

def create_test_user(email):
    # Properly hash password using your actual pwd_context
    hashed_password = pwd_context.hash(ACTUAL_PASSWORD)
    with Session(engine) as session:
        user = User(email=email, password_hash=hashed_password, name="Tester")
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

def create_app_for_user(user, status="pending"):
    applied_dt = datetime.fromisoformat("2025-11-01T10:00:00")
    followup_dt = datetime.fromisoformat("2025-11-10T10:00:00")
    with Session(engine) as session:
        app_obj = Application(
            user_id=user.id,
            company_name="TestCorp",
            role_title="Engineer",
            city="Metropolis",
            country="Countryland",
            applied_date=applied_dt,
            followup_date=followup_dt,
            status=status
        )
        session.add(app_obj)
        session.commit()
        session.refresh(app_obj)
        return app_obj

def get_token_for_user(user):
    resp = client.post("/login", json={"email": user.email, "password": ACTUAL_PASSWORD})
    assert resp.status_code == 200
    return resp.json()["token"]

@pytest.fixture(scope="function")
def seeded_user_and_apps():
    # Use a random email for each test run, so no collision
    email = f"testuser_{uuid.uuid4().hex}@example.com"

    # Clean up user (should not exist, but just in case)
    with Session(engine) as session:
        session.exec(delete(User).where(User.email == email))
        session.commit()

    user = create_test_user(email)
    create_app_for_user(user, status="pending")
    create_app_for_user(user, status="active")
    create_app_for_user(user, status="rejected")
    return user

def test_metrics_endpoint(seeded_user_and_apps):
    user = seeded_user_and_apps
    token = get_token_for_user(user)
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.get("/metrics", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["applications_total"] == 3
    for status in ["pending", "active", "rejected"]:
        assert status in data["applications_by_status"]
        assert data["applications_by_status"][status] == 1

def test_apps_export_csv(seeded_user_and_apps):
    user = seeded_user_and_apps
    token = get_token_for_user(user)
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.get("/apps", headers=headers)
    assert resp.status_code == 200
    apps = resp.json()
    assert isinstance(apps, list)
    assert len(apps) == 3
    df = pd.DataFrame(apps)
    csv_data = df.to_csv(index=False)
    assert "company_name" in csv_data
    assert "role_title" in csv_data
