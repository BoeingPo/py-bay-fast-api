from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.entities import user  # noqa: F401 — registers User table with Base
from app.infrastructure.db.dynamo_init import init_dynamo_tables
from app.infrastructure.db.postgres import Base, engine
from app.interface_adapters.controllers import bookings, concerts, health, users

# All routes/repositories below are deliberately plain `def`, not `async def`: Postgres access goes
# through psycopg2 and DynamoDB through boto3, both blocking. FastAPI runs sync path operations in a
# threadpool automatically, so this avoids ever blocking the event loop without needing async drivers.

app = FastAPI(title="Concert Booking API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(users.router)
app.include_router(concerts.router)
app.include_router(bookings.router)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    init_dynamo_tables()
