# profiler-service/main.py
from fastapi import FastAPI, HTTPException
from sqlmodel import SQLModel, Field, create_engine, Session, select
from pydantic import BaseModel
from datetime import datetime

DB_FILE = "profiler.db"
engine = create_engine(
    f"sqlite:///{DB_FILE}", connect_args={"check_same_thread": False}
)


class Parcel(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    trigger_id: str
    barcode: str | None
    dimension: str | None
    weight: str | None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ParcelIn(BaseModel):
    trigger_id: str
    barcode: str | None = None
    dimension: str | None = None
    weight: str | None = None


app = FastAPI(title="profiler-service")


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)


@app.post("/parcels", status_code=201)
def create_parcel(payload: ParcelIn):
    with Session(engine) as s:
        parcel = Parcel(**payload.dict())
        s.add(parcel)
        s.commit()
        s.refresh(parcel)
        return parcel


@app.get("/parcels")
def list_parcels():
    with Session(engine) as s:
        q = s.exec(select(Parcel).order_by(Parcel.created_at.desc()))
        return q.all()
