# app/services/user_service.py

from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.schemas.user import UserCreate
from app.utils.security import get_password_hash, verify_password


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_by_username_or_email(self, identifier: str) -> User | None:
        return self.db.query(User).filter(
            (User.username == identifier) | (User.email == identifier)
        ).first()

    def register_user(self, user_data: UserCreate) -> User:
        if self.get_by_username_or_email(user_data.username) or \
                self.get_by_username_or_email(str(user_data.email)):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username or email already exists"
            )

        new_user = User(
            username=user_data.username,
            email=str(user_data.email),
            password_hash=get_password_hash(user_data.password)
        )

        try:
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)
        except Exception:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )

        return new_user

    def authenticate_user(self, username_or_email: str, password: str) -> User:
        user = self.get_by_username_or_email(username_or_email)

        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is disabled"
            )

        user.last_login = datetime.now()
        self.db.commit()

        return user
