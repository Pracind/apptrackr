from sqlmodel import Session, select
from db import engine
from models import User, Application

with Session(engine) as session:
    users = session.exec(select(User)).all()
    apps = session.exec(select(Application)).all()

    print("Users:")
    for user in users:
        print(user)

    print("\nApplications:")
    for app in apps:
        print(app)
