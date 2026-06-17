from fastapi import Depends
from sqlalchemy.orm import Session

from app.entities.user import User
from app.infrastructure.db.postgres import get_db


class UserRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, user_id: int) -> User | None:
        return self._db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> User | None:
        return self._db.query(User).filter(User.email == email).first()

    def create(self, email: str, name: str, hashed_password: str) -> User:
        user = User(email=email, name=name, hashed_password=hashed_password)
        self._db.add(user)
        self._db.commit()
        self._db.refresh(user)
        return user


def get_user_repo(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)
