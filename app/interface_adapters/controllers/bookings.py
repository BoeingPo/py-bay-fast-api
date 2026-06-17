from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.entities.user import User
from app.exceptions import BookingCancelError, BookingNotFoundError, InsufficientSeatsError
from app.infrastructure.auth import get_current_user
from app.schemas.booking import BookingCreate, BookingResponse
from app.use_cases.booking_use_cases import BookingUseCases, get_booking_use_cases

router = APIRouter(tags=["bookings"])


@router.post("/concerts/{concert_id}/book", response_model=BookingResponse, status_code=201)
def book_seats(
    concert_id: str,
    body: BookingCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    uc: BookingUseCases = Depends(get_booking_use_cases),
):
    try:
        return uc.book_seats(concert_id, current_user.id, body.seats_count)
    except InsufficientSeatsError:
        raise HTTPException(status_code=409, detail="Not enough seats available")


@router.get("/bookings/", response_model=list[BookingResponse])
def list_bookings(
    user_id: int | None = Query(default=None),
    concert_id: str | None = Query(default=None),
    uc: BookingUseCases = Depends(get_booking_use_cases),
):
    return uc.list_bookings(user_id, concert_id)


@router.get("/bookings/{booking_id}", response_model=BookingResponse)
def get_booking(booking_id: str, uc: BookingUseCases = Depends(get_booking_use_cases)):
    try:
        return uc.get_booking(booking_id)
    except BookingNotFoundError:
        raise HTTPException(status_code=404, detail="Booking not found")


@router.delete("/bookings/{booking_id}", status_code=204)
def cancel_booking(
    booking_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    uc: BookingUseCases = Depends(get_booking_use_cases),
):
    try:
        uc.cancel_booking(booking_id, current_user.id)
    except BookingCancelError:
        raise HTTPException(status_code=409, detail="Booking not found, already cancelled, or not yours")
