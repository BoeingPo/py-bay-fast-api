from fastapi import APIRouter, Depends, HTTPException

from app.exceptions import ConcertNotFoundError
from app.schemas.concert import ConcertCreate, ConcertResponse
from app.use_cases.concert_use_cases import ConcertUseCases, get_concert_use_cases

router = APIRouter(prefix="/concerts", tags=["concerts"])


@router.get("/", response_model=list[ConcertResponse])
def list_concerts(uc: ConcertUseCases = Depends(get_concert_use_cases)):
    return uc.list_concerts()


@router.get("/{concert_id}", response_model=ConcertResponse)
def get_concert(concert_id: str, uc: ConcertUseCases = Depends(get_concert_use_cases)):
    try:
        return uc.get_concert(concert_id)
    except ConcertNotFoundError:
        raise HTTPException(status_code=404, detail="Concert not found")


@router.post("/", response_model=ConcertResponse, status_code=201)
def create_concert(body: ConcertCreate, uc: ConcertUseCases = Depends(get_concert_use_cases)):
    return uc.create_concert(body)
