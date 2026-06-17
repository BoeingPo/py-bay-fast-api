from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.entities.user import User
from app.exceptions import DuplicateEmailError, InvalidCredentialsError
from app.infrastructure.auth import create_access_token, get_current_user
from app.schemas.user import Token, UserCreate, UserResponse
from app.use_cases.user_use_cases import UserUseCases, get_user_use_cases

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(body: UserCreate, uc: UserUseCases = Depends(get_user_use_cases)):
    try:
        return uc.register(body.email, body.name, body.password)
    except DuplicateEmailError:
        raise HTTPException(status_code=409, detail="Email already registered")


@router.post("/login", response_model=Token)
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], uc: UserUseCases = Depends(get_user_use_cases)):
    try:
        user = uc.authenticate(form.username, form.password)
    except InvalidCredentialsError:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    return Token(access_token=create_access_token(user.id))


@router.get("/me", response_model=UserResponse)
def get_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user
