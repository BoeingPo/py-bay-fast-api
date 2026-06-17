from fastapi import Depends

from app.exceptions import ConcertNotFoundError
from app.interface_adapters.repositories.concert_repository import ConcertRepository, get_concert_repo
from app.schemas.concert import ConcertCreate


class ConcertUseCases:
    def __init__(self, repo: ConcertRepository) -> None:
        self._repo = repo

    def list_concerts(self) -> list[dict]:
        return self._repo.list_all()

    def get_concert(self, concert_id: str) -> dict:
        concert = self._repo.get_by_id(concert_id)
        if not concert:
            raise ConcertNotFoundError()
        return concert

    def create_concert(self, data: ConcertCreate) -> dict:
        return self._repo.create(data.model_dump())


def get_concert_use_cases(repo: ConcertRepository = Depends(get_concert_repo)) -> ConcertUseCases:
    return ConcertUseCases(repo)
