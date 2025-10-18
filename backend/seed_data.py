from sqlmodel import Session
from db import engine
from models import User, Application
from datetime import datetime, timedelta

def seed():
    with Session(engine) as session:
        # Create demo user
        user = User(email="demo@example.com", password_hash="fakehash", name="Demo User")
        session.add(user)
        session.commit()  # Get the auto-generated user.id

        # Create multiple demo applications
        demo_apps = [
            Application(
                user_id=user.id,
                company_name="FinTech Bros",
                role_title="Backend Developer",
                city="Bangalore",
                country="India",
                salary="Comp",
                applied_date=datetime.utcnow(),
                followup_date=datetime.utcnow() + timedelta(days=7),
                status="pending",
                followup_method="email",
                notes="Applied via company portal."
            ),
            Application(
                user_id=user.id,
                company_name="CloudWorks",
                role_title="SWE",
                city="Remote",
                country="India",
                salary="Unknown",
                applied_date=datetime.utcnow() - timedelta(days=8),
                followup_date=datetime.utcnow() - timedelta(days=1),
                status="followed-up",
                followup_method="LinkedIn",
                notes="Follow-up sent after HR responded."
            ),
            Application(
                user_id=user.id,
                company_name="BigData Group",
                role_title="Data Engineer",
                city="Mumbai",
                country="India",
                salary="900000",
                applied_date=datetime.utcnow() - timedelta(days=15),
                followup_date=datetime.utcnow() - timedelta(days=8),
                status="not-responded",
                followup_method="email",
                notes="Sent follow-up, no reply."
            )
        ]

        session.add_all(demo_apps)
        session.commit()
        print("Demo user & applications seeded.")

if __name__ == "__main__":
    seed()
