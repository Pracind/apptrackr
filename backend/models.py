from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field

class Application(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")

    company_name: str
    role_title: str
    city: str
    country: str

    # Salary can store "Comp", "Unknown", or a number as string
    salary: Optional[str] = None

    applied_date: datetime
    followup_date: Optional[datetime] = None

    # Choices: "pending", "followed-up", "not-responded", "rejected", "accepted"
    status: str = Field(default="pending")
    followup_method: Optional[str] = None  # e.g. "email", "portal", "LinkedIn"

    notes: Optional[str] = None

    updated_at: datetime = Field(default_factory=datetime.utcnow)
    # timeline_events would need table (can be added later)

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    password_hash: str
    name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)


