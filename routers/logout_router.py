from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status, HTTPException

from sql.models import User
from controllers.db import get_db
from controllers.oauth2 import oauth2_scheme
from controllers.user import get_current_user
from message import UNKNOWN_REFRESH_TOKEN, LOGOUT
from crud.token import has_user_refresh_token, delete_user_refresh_token


router = APIRouter(prefix="", tags=["auth"])


@router.delete(
    path="/logout",
    summary="Выход пользователя",
    status_code=status.HTTP_200_OK,
    response_description=LOGOUT)
async def logout_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
    user: User = Depends(get_current_user)
):
    if not has_user_refresh_token(db, user.id, token):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=UNKNOWN_REFRESH_TOKEN)

    delete_user_refresh_token(db, user.id, token)
