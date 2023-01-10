from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status

from sql import models
from sql.crud import delete_user_refresh_token
from controllers.db import get_db
from controllers.oauth2 import oauth2_scheme
from controllers.user import get_current_user


router = APIRouter()


@router.delete(path="/logout", tags=["auth"], summary="Logout user")
async def logout_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
    user: models.User = Depends(get_current_user)
):
    user_refresh_tokens = [value.refresh_token for value in user.refresh_tokens]  # type: ignore
    if token not in user_refresh_tokens:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unknown refresh token"
        )
    
    delete_user_refresh_token(db, user.id, token)
