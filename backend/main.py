from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session
import models
from database import Base, engine, get_db
from routers import clients, sessions, registrations, payments
import crud
import schemas
from services.scheduler import start_scheduler, stop_scheduler
from config import settings

Base.metadata.create_all(bind=engine)

# Lightweight migrations — add new columns if they don't exist yet
_MIGRATIONS = [
    "ALTER TABLE sessions ADD COLUMN price_per_month REAL DEFAULT 0.0",
]
with engine.connect() as _conn:
    for _sql in _MIGRATIONS:
        try:
            _conn.execute(text(_sql))
            _conn.commit()
        except Exception:
            pass

app = FastAPI(title="Fitness Studio API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://tzipi-helfer-studio.vercel.app", settings.frontend_url.rstrip("/") if hasattr(settings, "frontend_url") else "http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(clients.router, prefix="/api")
app.include_router(sessions.router, prefix="/api")
app.include_router(registrations.router, prefix="/api")
app.include_router(payments.router, prefix="/api")


@app.on_event("startup")
def startup():
    start_scheduler()


@app.on_event("shutdown")
def shutdown():
    stop_scheduler()


@app.get("/api/dashboard", response_model=schemas.DashboardStats)
def dashboard(db: Session = Depends(get_db)):
    return crud.get_dashboard_stats(db)


@app.get("/")
def root():
    return {"status": "ok", "docs": "/docs"}
