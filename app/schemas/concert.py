from pydantic import BaseModel


class ConcertCreate(BaseModel):
    name: str
    venue: str
    date: str  # ISO 8601 e.g. "2026-08-01T19:00:00"
    total_seats: int
    price: float


class ConcertResponse(ConcertCreate):
    id: str
    available_seats: int
