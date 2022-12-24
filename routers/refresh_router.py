from datetime import timedelta
from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from sql import models
from sql.crud import (
    delete_user_refresh_token,
    delete_all_user_refresh_token
    )
from models import schemas
from controllers.db import get_db
from controllers.oauth2 import oauth2_scheme
from controllers.user import get_current_user
from controllers.token import create_access_token, create_refresh_token
from sql.crud import create_user_refresh_token, create_user_white_ip
from config import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS


router = APIRouter()


@router.post("/refresh", tags=["auth"], response_model=schemas.Token)
async def refresh_tokens(
    request: Request,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
    user: models.User = Depends(get_current_user),
    ):
    white_ip = request.client.host  # type: ignore
    user_white_list_ip = [value.white_ip for value in user.white_list_ip]  # type: ignore
    if white_ip not in user_white_list_ip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unknown IP"
        )

    user_refresh_tokens = [value.refresh_token for value in user.refresh_tokens]  # type: ignore
    if token not in user_refresh_tokens:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unknown refresh token"
        )
    
    if len(user_refresh_tokens) > 10:
        delete_all_user_refresh_token(db, user.id)
    else:
        delete_user_refresh_token(db, user.id, token)

    token_data = {"sub": user.email}

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(token_data, expires_delta=access_token_expires)

    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_refresh_token(token_data, expires_delta=refresh_token_expires)
    create_user_refresh_token(db, user.id, refresh_token)
    
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}