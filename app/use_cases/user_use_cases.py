from fastapi import Depends

from app.entities.user import User
from app.exceptions import DuplicateEmailError, InvalidCredentialsError
from app.infrastructure.auth import hash_password, verify_password
from app.interface_adapters.repositories.user_repository import UserRepository, get_user_repo


class UserUseCases:
    def __init__(self, repo: UserRepository) -> None:
        self._repo = repo

    def register(self, email: str, name: str, password: str) -> User:
        if self._repo.get_by_email(email):
            raise DuplicateEmailError()
        return self._repo.create(email, name, hash_password(password))

    def authenticate(self, email: str, password: str) -> User:
        user = self._repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError()
        return user


def get_user_use_cases(repo: UserRepository = Depends(get_user_repo)) -> UserUseCases:
    return UserUseCases(repo)
