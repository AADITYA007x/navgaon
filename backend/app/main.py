import os
import json
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from .database import get_db, SessionLocal, Base, engine
from .models import City, Neighborhood, Building, Resident, Event, Newspaper
from .simulation import advance_day
from .generate import generate_city
from .newspaper import write_edition
from .actions import list_actions, apply_action

load_dotenv()
AUTO_RUN_MINUTES = float(os.getenv("AUTO_RUN_MINUTES", "0"))
scheduler = BackgroundScheduler()


def auto_advance():
    db = SessionLocal()
    try:
        day = advance_day(db)
        write_edition(db, day)
        print(f"Auto-run: advanced to day {day}")
    except Exception as e:
        print("Auto-run error:", e)
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app):
    Base.metadata.create_all(engine)
    db = SessionLocal()
    try:
        has_city = db.scalar(select(City)) is not None
    finally:
        db.close()
    if not has_city:
        generate_city()

    if AUTO_RUN_MINUTES > 0:
        scheduler.add_job(
            auto_advance,
            "interval",
            minutes=AUTO_RUN_MINUTES,
            id="auto_advance",
            max_instances=1,
            coalesce=True,
        )
        scheduler.start()
    yield
    if scheduler.running:
        scheduler.shutdown(wait=False)

app = FastAPI(title="Navgaon API", lifespan=lifespan)
ALLOWED_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]
if os.getenv("FRONTEND_URL"):
    ALLOWED_ORIGINS.append(os.getenv("FRONTEND_URL").rstrip("/"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

def to_dict(obj):
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


def paper_dict(p):
    return {"day": p.day, "headline": p.headline, "articles": json.loads(p.content)}


@app.get("/")
def root():
    return {"message": "Welcome to Navgaon"}


@app.get("/city")
def get_city(db: Session = Depends(get_db)):
    city = db.scalar(select(City))
    if not city:
        return {"error": "No city generated yet"}
    return to_dict(city)


@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    alive = Resident.alive == True
    return {
        "day": db.scalar(select(City.day)),
        "population": db.scalar(select(func.count()).select_from(Resident).where(alive)),
        "unemployed": db.scalar(select(func.count()).select_from(Resident).where(alive, Resident.job == "Unemployed")),
        "married": db.scalar(select(func.count()).select_from(Resident).where(alive, Resident.partner_id != None)),
        "open_shops": db.scalar(select(func.count()).select_from(Building).where(Building.kind == "shop", Building.is_open == True)),
        "total_events": db.scalar(select(func.count()).select_from(Event)),
    }


@app.get("/neighborhoods")
def get_neighborhoods(db: Session = Depends(get_db)):
    return [to_dict(n) for n in db.scalars(select(Neighborhood))]


@app.get("/buildings")
def get_buildings(db: Session = Depends(get_db)):
    return [to_dict(b) for b in db.scalars(select(Building))]


@app.get("/residents")
def get_residents(limit: int = 50, db: Session = Depends(get_db)):
    query = select(Resident).where(Resident.alive == True).limit(limit)
    return [to_dict(r) for r in db.scalars(query)]


@app.get("/residents/{resident_id}")
def get_resident(resident_id: int, db: Session = Depends(get_db)):
    r = db.get(Resident, resident_id)
    if not r:
        return {"error": "Resident not found"}
    return to_dict(r)


@app.get("/events")
def get_events(day: int | None = None, limit: int = 100, db: Session = Depends(get_db)):
    query = select(Event).order_by(Event.day.desc(), Event.id.desc()).limit(limit)
    if day is not None:
        query = query.where(Event.day == day)
    return [to_dict(e) for e in db.scalars(query)]


@app.post("/simulate/next-day")
def next_day(db: Session = Depends(get_db)):
    day = advance_day(db)
    events = [to_dict(e) for e in db.scalars(select(Event).where(Event.day == day))]
    paper = write_edition(db, day)
    return {"day": day, "events": events, "newspaper": paper_dict(paper)}


@app.post("/simulate/{days}")
def simulate_days(days: int, db: Session = Depends(get_db)):
    days = max(1, min(days, 30))
    day = None
    for _ in range(days):
        day = advance_day(db)
    return {"day": day, "simulated": days}


@app.post("/reset")
def reset(seed: int | None = None):
    generate_city(seed=seed)
    return {"message": "City regenerated"}


@app.get("/newspaper/latest")
def latest_newspaper(db: Session = Depends(get_db)):
    day = db.scalar(select(City.day))
    return paper_dict(write_edition(db, day))


@app.get("/newspaper/{day}")
def newspaper_for_day(day: int, db: Session = Depends(get_db)):
    current = db.scalar(select(City.day))
    if day < 1 or day > current:
        return {"error": "That day hasn't happened yet"}
    return paper_dict(write_edition(db, day))


@app.post("/newspaper/{day}/rewrite")
def rewrite_newspaper(day: int, db: Session = Depends(get_db)):
    existing = db.scalar(select(Newspaper).where(Newspaper.day == day))
    if existing:
        db.delete(existing)
        db.commit()
    return paper_dict(write_edition(db, day))


@app.get("/actions")
def get_actions(db: Session = Depends(get_db)):
    return list_actions(db)


@app.post("/actions/{key}")
def do_action(key: str, db: Session = Depends(get_db)):
    return apply_action(db, key)


@app.get("/autorun")
def get_autorun():
    job = scheduler.get_job("auto_advance") if scheduler.running else None
    return {
        "enabled": job is not None,
        "minutes": AUTO_RUN_MINUTES,
        "next_run": job.next_run_time.isoformat() if job else None,
    }


CRON_SECRET = os.getenv("CRON_SECRET", "")


@app.get("/cron/advance")
def cron_advance(key: str = ""):
    if not CRON_SECRET or key != CRON_SECRET:
        raise HTTPException(status_code=403, detail="Forbidden")
    auto_advance()
    return {"ok": True}