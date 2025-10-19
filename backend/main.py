from fastapi import FastAPI, HTTPException
from sqlmodel import Session, select
from backend.db import engine, create_db_and_tables
from backend.models import User, Application
from passlib.context import CryptContext
from pydantic import BaseModel
import jwt
from datetime import datetime, timedelta

SECRET_KEY = "superdupersecret"



# Call this once at startup
create_db_and_tables()


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class SignupRequest(BaseModel):
    email: str
    password: str
    name: str

class LoginRequest(BaseModel):
    email: str
    password: str

app = FastAPI()

@app.post("/signup")
def signup(user: SignupRequest):
    # Hash the password
    hashed_password = pwd_context.hash(user.password[:72])
    # Check if email already exists
    with Session(engine) as session:
        existing_user = session.exec(
            select(User).where(User.email == user.email)
        ).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered.")
        # Create user record
        new_user = User(
            email=user.email,
            password_hash=hashed_password,
            name=user.name
        )
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return {"id": new_user.id, "email": new_user.email, "name": new_user.name}
    
@app.post("/login")
def login(request: LoginRequest):
    with Session(engine) as session:
        user = session.exec(
            select(User).where(User.email == request.email)
        ).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        if not pwd_context.verify(request.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        # Create JWT token
        payload = {
            "sub": user.id,
            "exp": datetime.utcnow() + timedelta(hours=1),   # expires in 1 hour
            "email": user.email,
            "name": user.name,
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        return {"token": token, "user": {"id": user.id, "email": user.email}}
    



