from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status

from sql.models import User
from models.schemas import UserOut, UserUpdate
from crud.user import update_user
from controllers.db import get_db
from controllers.user import get_current_user, get_valid_user


router = APIRouter(prefix="/user", tags=["user"])


@router.get(
    path="/me",
    summary="Отдаёт информацию о пользователе с помощью access токена",
    status_code=status.HTTP_200_OK,
    response_model=UserOut)
async def read_user(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    return get_valid_user(db, user)


@router.patch(
    path="/update",
    summary="Обновляет имя и фамилию пользователя",
    status_code=status.HTTP_201_CREATED,
    response_model=UserOut)
async def update_user_information(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    update_user(db, user.id, user_data)
    return get_valid_user(db, user)
