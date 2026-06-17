import uuid
from datetime import datetime, timezone

from fastapi import Depends

from app.exceptions import BookingNotFoundError
from app.interface_adapters.repositories.booking_repository import BookingRepository, get_booking_repo
from app.interface_adapters.repositories.concert_repository import ConcertRepository, get_concert_repo


class BookingUseCases:
    def __init__(self, booking_repo: BookingRepository, concert_repo: ConcertRepository) -> None:
        self._booking_repo = booking_repo
        self._concert_repo = concert_repo

    def book_seats(self, concert_id: str, user_id: int, seats_count: int) -> dict:
        self._concert_repo.decrement_seats(concert_id, seats_count)
        booking = {
            "id": str(uuid.uuid4()),
            "concert_id": concert_id,
            "user_id": user_id,
            "seats_count": seats_count,
            "status": "confirmed",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        return self._booking_repo.create(booking)

    def cancel_booking(self, booking_id: str, user_id: int) -> None:
        booking = self._booking_repo.cancel(booking_id, user_id)
        self._concert_repo.increment_seats(booking["concert_id"], booking["seats_count"])

    def get_booking(self, booking_id: str) -> dict:
        booking = self._booking_repo.get_by_id(booking_id)
        if not booking:
            raise BookingNotFoundError()
        return booking

    def list_bookings(self, user_id: int | None, concert_id: str | None) -> list[dict]:
        if user_id is not None:
            return self._booking_repo.list_by_user(user_id)
        if concert_id is not None:
            return self._booking_repo.list_by_concert(concert_id)
        return self._booking_repo.list_all()


def get_booking_use_cases(
    booking_repo: BookingRepository = Depends(get_booking_repo),
    concert_repo: ConcertRepository = Depends(get_concert_repo),
) -> BookingUseCases:
    return BookingUseCases(booking_repo, concert_repo)
