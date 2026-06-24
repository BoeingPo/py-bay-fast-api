from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm

from app.config import settings
from app.entities.user import User
from app.exceptions import DuplicateEmailError, InvalidCredentialsError
from app.infrastructure.auth import COOKIE_NAME, create_access_token, get_current_user
from app.schemas.user import UserCreate, UserResponse
from app.use_cases.user_use_cases import UserUseCases, get_user_use_cases

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(body: UserCreate, uc: UserUseCases = Depends(get_user_use_cases)):
    try:
        return uc.register(body.email, body.name, body.password)
    except DuplicateEmailError:
        raise HTTPException(status_code=409, detail="Email already registered")


@router.post("/login", response_model=UserResponse)
def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    response: Response,
    uc: UserUseCases = Depends(get_user_use_cases),
):
    try:
        user = uc.authenticate(form.username, form.password)
    except InvalidCredentialsError:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    response.set_cookie(
        key=COOKIE_NAME,
        value=create_access_token(user.id),
        httponly=True,
        samesite="lax",
        secure=settings.cookie_secure,
        max_age=settings.jwt_expire_minutes * 60,
    )
    return user


@router.post("/logout", status_code=204)
def logout(response: Response):
    response.delete_cookie(COOKIE_NAME)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user
