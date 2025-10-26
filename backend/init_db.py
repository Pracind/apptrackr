from models import User, Application, CronLog  
from db import create_db_and_tables

if __name__ == "__main__":
    create_db_and_tables()
    print("Database and tables created successfully.")
