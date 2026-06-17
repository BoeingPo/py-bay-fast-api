from pydantic import BaseModel


class BookingCreate(BaseModel):
    seats_count: int


class BookingResponse(BaseModel):
    id: str
    concert_id: str
    user_id: int
    seats_count: int
    status: str  # "confirmed" | "cancelled"
    created_at: str
