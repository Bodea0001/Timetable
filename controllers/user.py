import jwt
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer
from fastapi import Depends, HTTPException, status

from sql.models import User
from controllers.db import get_db
from controllers.oauth2 import oauth2_scheme
from controllers.application import (
    get_valid_user_applications,
    get_valid_applications_for_consideration, 
)
from controllers.timetable import get_valid_timetables
from controllers.password import get_password_hash, verify_password
from crud.user import get_user, create_user_in_db
from crud.token import get_amount_of_user_refresh_tokens
from config import SECRET_KEY, ALGORITHM, REFRESH_TOKEN_LIMIT
from models.schemas import TokenData, UserOut, OAuth2PasswordRequestFormUpdate


def authenticate_user(db: Session, username: str, password: str):
    "Аутентифицирует пользователя"
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.password):  # type: ignore
        return False
    return user


async def get_current_user(
        db: Session = Depends(get_db),token: str = Depends(oauth2_scheme)
    ) -> User:
    "С помощью информации в токене находит и отдает информацию о пользователе"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"})

    try:
        payload = jwt.decode(token, SECRET_KEY, [ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.PyJWTError:
        raise credentials_exception

    user = get_user(db, username=token_data.username)
    if not user:
        raise credentials_exception
    return user


def get_valid_user(db: Session, user: User) -> UserOut:
    "Отдаёт информацию о пользователе в нормальном виде"
    timetables = get_valid_timetables(db, user.timetables_info, user.id)  # type: ignore
    user_applications = get_valid_user_applications(db, user.applications)  # type: ignore
    apps_for_consideration = get_valid_applications_for_consideration(db, user.id)
    return UserOut(
        id=user.id, # type: ignore
        email=user.email, # type: ignore 
        first_name=user.first_name, # type: ignore
        last_name=user.last_name, # type: ignore
        tg_user_id=user.tg_user_id,  # type: ignore
        user_applications=user_applications,  
        applications_for_consideration=apps_for_consideration,
        timetables_info=timetables
    )


def is_user_refresh_tokens_limit_exceeded(
        db: Session, user_id: int | Column[Integer]) -> bool:
    """Проверяет, превышен ли лимит количества созданных пользователю 
    токенов"""
    refresh_tokens_count = get_amount_of_user_refresh_tokens(db, user_id)
    return refresh_tokens_count > REFRESH_TOKEN_LIMIT


def create_user(db: Session, data: OAuth2PasswordRequestFormUpdate):
    """Валидирует входные данные и отдает их для создания пользователя в БД"""
    data.password = get_password_hash(data.password)
    user = User(
        email=data.username,
        password=data.password,
        first_name=data.first_name.capitalize(),
        last_name=data.last_name.capitalize())
    return create_user_in_db(db, user)
