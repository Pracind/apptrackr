import pytest
from sqlmodel import Session, SQLModel, create_engine
from datetime import datetime, timedelta

from backend.models import Application, AppNotification, CronLog
from backend.main import run_cron_updates  # Import your function

@pytest.fixture
def test_engine():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    return engine

def create_sample_data(session, today):
    # Application that should move from "active" to "pending"
    app1 = Application(
        user_id=1,
        company_name="CompanyA",
        role_title="Engineer",
        city="CityA",
        country="CountryA",
        status="active",
        applied_date=today - timedelta(days=10),
        followup_date=today,
    )
    # Application that should move from "followed-up" to "not-responded"
    app2 = Application(
        user_id=1,
        company_name="CompanyB",
        role_title="Analyst",
        city="CityB",
        country="CountryB",
        status="followed-up",
        applied_date=today - timedelta(days=15),
        followup_date=today - timedelta(days=8),
        followed_up_at=datetime.utcnow() - timedelta(days=8),
    )
    session.add(app1)
    session.add(app2)
    session.commit()
    app1_id = app1.id
    app2_id = app2.id
    return app1_id, app2_id

def test_run_cron_updates_status_changes(test_engine):
    today = datetime.utcnow().date()
    # Add sample data and keep IDs only
    with Session(test_engine) as session:
        app1_id, app2_id = create_sample_data(session, today)

    # Run automation
    count = run_cron_updates(for_user_id=1, engine=test_engine)

    # Check results in a new session!
    with Session(test_engine) as session:
        app1_db = session.get(Application, app1_id)
        app2_db = session.get(Application, app2_id)
        assert app1_db.status == "pending"
        assert app2_db.status == "not-responded"

        notifs = session.query(AppNotification).all()
        assert len(notifs) == 2
        msgs = [n.message for n in notifs]
        assert any("Follow-up date reached" in m for m in msgs)
        assert any("No response after 7 days" in m for m in msgs)

    assert count == 2
