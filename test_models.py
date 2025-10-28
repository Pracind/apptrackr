import pytest
from sqlmodel import SQLModel, create_engine, Session
from backend.models import User, Application
from datetime import datetime

@pytest.fixture(name="session")
def session_fixture():
    # Use in-memory SQLite for testing (no file created)
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

def test_create_user(session):
    user = User(email="test@example.com", password_hash="abc123", name="Test User")
    session.add(user)
    session.commit()
    result = session.get(User, user.id)
    assert result is not None
    assert result.email == "test@example.com"
    assert result.is_active is True

def test_create_application(session):
    user = User(email="applicant@example.com", password_hash="pwhash")
    session.add(user)
    session.commit()
    app = Application(
        user_id=user.id,
        company_name="TestCorp",
        role_title="Engineer",
        city="TestCity",
        country="TestLand",
        applied_date=datetime.utcnow(),
        status="pending"
    )
    session.add(app)
    session.commit()
    result = session.get(Application, app.id)
    assert result is not None
    assert result.company_name == "TestCorp"
    assert result.user_id == user.id
    assert result.status == "pending"
