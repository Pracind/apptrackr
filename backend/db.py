from sqlmodel import SQLModel, create_engine

# SQLite URL (can also use environment variable for config)
DATABASE_URL = "sqlite:///apptrackr.db"

engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    