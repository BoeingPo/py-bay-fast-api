from fastapi import FastAPI

from app.entities import user  # noqa: F401 — registers User table with Base
from app.infrastructure.db.dynamo_init import init_dynamo_tables
from app.infrastructure.db.postgres import Base, engine
from app.interface_adapters.controllers import bookings, concerts, health, users

app = FastAPI(title="Concert Booking API", version="0.1.0")

app.include_router(health.router)
app.include_router(users.router)
app.include_router(concerts.router)
app.include_router(bookings.router)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    init_dynamo_tables()
