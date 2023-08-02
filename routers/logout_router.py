from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status

from sql import models
from sql.crud import delete_user_refresh_token
from controllers.db import get_db
from controllers.oauth2 import oauth2_scheme
from controllers.user import get_current_user, check_user_refresh_token


router = APIRouter()


@router.delete(
    path="/logout",
    tags=["auth"],
    summary="Выход пользователя",
    status_code=status.HTTP_200_OK)
async def logout_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
    user: models.User = Depends(get_current_user)
):
    check_user_refresh_token(token, user.refresh_tokens)  # type: ignore

    delete_user_refresh_token(db, user.id, token)
