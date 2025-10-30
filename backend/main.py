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
from apscheduler.schedulers.background import BackgroundScheduler
import logging
from backend.models import CronLog, AppNotification, Application
import dateutil.parser


logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

logging.getLogger("uvicorn").setLevel(logging.WARNING)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
logging.getLogger("apscheduler").setLevel(logging.WARNING)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
    followed_up_at: Optional[datetime] = None

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
        return {"token": token, "user": {"id": user.id, "email": user.email, "name": user.name}}
    

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
    
@app.get("/notifications")
def get_notifications(current_user: dict = Depends(get_current_user)):
    with Session(engine) as session:
        notifications = session.exec(
            select(AppNotification)
            .where(AppNotification.user_id == current_user["id"])
            .where(AppNotification.read == False)  # only unread
            .order_by(AppNotification.created_at.desc())
        ).all()
        return notifications
    
@app.post("/notifications/mark-read")
def mark_all_notifications_as_read(current_user: dict = Depends(get_current_user)):
    with Session(engine) as session:
        notifications = session.exec(
            select(AppNotification)
            .where(AppNotification.user_id == current_user["id"])
            .where(AppNotification.read == False)
        ).all()
        logger.info(f"Marking as read: {[n.id for n in notifications]}")
        for notif in notifications:
            notif.read = True
            session.add(notif)
        session.commit()
        return {"marked_read": len(notifications)}
    
@app.get("/debug/apps")
def debug_apps():
    with Session(engine) as session:
        apps = session.exec(select(Application)).all()
        result = []
        for a in apps:
            result.append({
                "id": a.id,
                "company": a.company_name,
                "role": a.role_title,
                "status": a.status,
                "followup_date": str(a.followup_date),
                "followed_up_at": str(a.followed_up_at) if hasattr(a, "followed_up_at") else None
            })
        return result


def run_cron_updates(for_user_id=None, engine=None):

    logger.info("APScheduler: Running automatic followup check…")
    from sqlmodel import Session, select
    from backend.models import Application, AppNotification, CronLog

    if engine is None:
        from backend.db import engine as default_engine
        engine = default_engine

    updated_count = 0
    today = datetime.utcnow().date()

    with Session(engine) as session:

        app_query = select(Application)
        if for_user_id:
            app_query = app_query.where(Application.user_id == int(for_user_id))

        # Move Active -> Pending
        active_apps = session.exec(select(Application).where(Application.status == "active")).all()
        #print("[DEBUG] active_apps list:", active_apps)

        for app in active_apps:
            if app.followup_date and app.followup_date.date() <= today:
                app.status = "pending"
                updated_count += 1

                notification = AppNotification(
                    app_id=app.id,
                    user_id=app.user_id,
                    message=f"Follow-up date reached for {app.company_name} - {app.role_title}",
                    created_at=datetime.utcnow()
                )
                session.add(notification)

        # Move Followed-up -> Not Responded after 7 days
        followed_up_apps = session.exec(select(Application).where(Application.status == "followed-up")).all()
        for app in followed_up_apps:
            logger.info(f"App {app.id}: status={app.status}, followed_up_at={app.followed_up_at} ({type(app.followed_up_at)})")
            fup = app.followed_up_at
            if fup:
                if isinstance(fup, str):
                    try:
                        fup = dateutil.parser.parse(fup)
                    except Exception as e:
                        logger.warning(f"App {app.id} has bad followed_up_at string: {app.followed_up_at}, skipping.")
                        continue
            
            print(datetime.utcnow())
            print(fup + timedelta(seconds = 7))
            print(datetime.utcnow() <= (fup + timedelta(seconds=7)))

            if datetime.utcnow() <= (fup + timedelta(seconds=7)):
                logger.info(f"Updating App {app.id} to not-responded")
                app.status = "not-responded"
                updated_count += 1

                notification = AppNotification(
                    app_id=app.id,
                    user_id=app.user_id,
                    message=f"No response from {app.company_name} - {app.role_title}",
                    created_at=datetime.utcnow()
                )
                session.add(notification)
        
        cron_entry = session.exec(select(CronLog).where(CronLog.job_name == "followup_check")).first()
        now = datetime.utcnow()
        if cron_entry:
            cron_entry.last_run = now
        else:
            cron_entry = CronLog(job_name="followup_check", last_run=now)
            session.add(cron_entry)

        session.commit()
    logger.info(f"[APScheduler] Updated {updated_count} applications via automation")
    return updated_count

@app.post("/automation/run-now")
def run_automation_now(current_user: dict = Depends(get_current_user)):
    count = run_cron_updates(for_user_id=current_user["id"])
    return {"processed": count}

@app.get("/cron/last-run")
def get_last_run():
    with Session(engine) as session:
        cron_entry = session.exec(select(CronLog).where(CronLog.job_name == "followup_check")).first()
        if cron_entry:
            return {"last_run": cron_entry.last_run.isoformat()}
        else:
            return {"last_run": None}
        

@app.get("/metrics")
def get_app_metrics(current_user: dict = Depends(get_current_user)):
    with Session(engine) as session:
        total_apps = len(list(session.exec(
            select(Application).where(Application.user_id == current_user["id"])
        )))
        statuses = ["pending", "active", "followed-up", "not-responded", "rejected"]
        status_counts = {}
        for status in statuses:
            status_counts[status] = len(list(session.exec(
                select(Application).where(
                    Application.user_id == current_user["id"],
                    Application.status == status
                )
            )))
    return {
        "applications_total": total_apps,
        "applications_by_status": status_counts,
    }

scheduler = None

@app.on_event("startup")
async def startup_event():
    global scheduler
    logger.info("FastAPI: Starting up and initializing scheduler...")
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_cron_updates, 'interval', seconds = 10)
    scheduler.start()
    logger.info("FastAPI: Scheduler started successfully!")

@app.on_event("shutdown")
async def shutdown_event():
    global scheduler
    if scheduler:
        logger.info("FastAPI: Shutting down scheduler...")
        scheduler.shutdown()

    



