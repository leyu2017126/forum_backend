# app/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import UserCreate, UserOut, Token
from app.utils.security import create_access_token
from app.services.user_service import UserService

router = APIRouter(tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    responses={
        409: {"description": "Username or email already exists"},
        400: {"description": "Invalid input data"},
        500: {"description": "Server error during user creation"}
    }
)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    service = UserService(db)
    new_user = service.register_user(user)
    return new_user


@router.post(
    "/login",
    response_model=Token,
    summary="User login",
    responses={
        401: {"description": "Invalid credentials"},
        403: {"description": "User account is disabled"},
    }
)
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    service = UserService(db)
    user = service.authenticate_user(form_data.username, form_data.password)

    token_data = {"sub": str(user.email)}
    access_token = create_access_token(data=token_data)

    return {"access_token": access_token, "token_type": "bearer"}
