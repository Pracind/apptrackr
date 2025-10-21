from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select
from backend.db import engine, create_db_and_tables
from backend.models import User, Application
from passlib.context import CryptContext
from pydantic import BaseModel
import jwt
from typing import Optional
from datetime import datetime, timedelta

SECRET_KEY = "superdupersecret"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Call this once at startup
create_db_and_tables()


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        email = payload.get("email")
        if user_id is None or email is None:
            raise credentials_exception
        # Optionally query the DB for real user object here!
        return {"id": user_id, "email": email, "name": payload.get("name")}
    except jwt.PyJWTError:
        raise credentials_exception
    

class CreateAppRequest(BaseModel):
    company_name: str
    role_title: str
    city: str
    country: str
    salary: Optional[str] = None
    applied_date: datetime
    followup_date: Optional[datetime] = None
    status: str = "pending"
    followup_method: Optional[str] = None
    notes: Optional[str] = None

class UpdateAppRequest(BaseModel):
    company_name: Optional[str] = None
    role_title: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    salary: Optional[str] = None
    applied_date: Optional[datetime] = None
    followup_date: Optional[datetime] = None
    status: Optional[str] = None
    followup_method: Optional[str] = None
    notes: Optional[str] = None

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
    

@app.get("/me")
def read_me(current_user: dict = Depends(get_current_user)):
    return {"user": current_user}


@app.get("/apps")
def get_apps(current_user: dict = Depends(get_current_user)):
    with Session(engine) as session:
        apps = session.exec(
            select(Application).where(Application.user_id == current_user["id"])
        ).all()
        return apps

@app.post("/apps")
def create_app(
    app_in: CreateAppRequest,
    current_user: dict = Depends(get_current_user)
):
    with Session(engine) as session:
        new_app = Application(
            user_id=current_user["id"],
            company_name=app_in.company_name,
            role_title=app_in.role_title,
            city=app_in.city,
            country=app_in.country,
            salary=app_in.salary,
            applied_date=app_in.applied_date,
            followup_date=app_in.followup_date,
            status=app_in.status,
            followup_method=app_in.followup_method,
            notes=app_in.notes,
        )
        session.add(new_app)
        session.commit()
        session.refresh(new_app)
        return new_app

@app.put("/apps/{id}")
def update_app(id: int, app_in: UpdateAppRequest, current_user: dict = Depends(get_current_user)):
    with Session(engine) as session:
        db_app = session.get(Application, id)
        if not db_app or db_app.user_id != current_user["id"]:
            raise HTTPException(status_code=404, detail="Application not found")
        app_data = app_in.dict(exclude_unset=True)
        for key, value in app_data.items():
            setattr(db_app, key, value)
        db_app.updated_at = datetime.utcnow()
        session.add(db_app)
        session.commit()
        session.refresh(db_app)
        return db_app
    
@app.delete("/apps/{id}")
def delete_app(id: int, current_user: dict = Depends(get_current_user)):
    with Session(engine) as session:
        db_app = session.get(Application, id)
        if not db_app or db_app.user_id != current_user["id"]:
            raise HTTPException(status_code=404, detail="Application not found")
        session.delete(db_app)
        session.commit()
        return {"detail": "Application deleted"}

    



