from datetime import timedelta
from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from models.schemas import Token
from controllers.user import authenticate_user
from controllers.token import create_access_token, create_refresh_token
from controllers.db import get_db
from sql.crud import create_user_refresh_token, create_user_white_ip, delete_all_user_refresh_token
from config import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS


router = APIRouter()


@router.post("/login", tags=["auth"], response_model=Token)
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    ):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_refresh_tokens = [value.refresh_token for value in user.refresh_tokens]  # type: ignore
    if len(user_refresh_tokens) > 10:
        delete_all_user_refresh_token(db, user.id)

    token_data = {"sub": user.email}

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(token_data, expires_delta=access_token_expires)

    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_refresh_token(token_data, expires_delta=refresh_token_expires)
    create_user_refresh_token(db, user.id, refresh_token)

    white_ip = request.client.host  # type: ignore
    user_white_list_ip = [value.white_ip for value in user.white_list_ip]  # type: ignore
    if white_ip not in user_white_list_ip:
        create_user_white_ip(db, user.id, white_ip)
    
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}