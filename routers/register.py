from datetime import timedelta
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status, HTTPException, Request

from sql import models
from sql.crud import create_user, create_user_refresh_token, create_user_white_ip
from models import schemas
from controllers.db import get_db
from controllers.user import get_user
from controllers.email import is_email_valid
from controllers.token import create_access_token, create_refresh_token
from controllers.password import get_password_hash
from config import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS

router = APIRouter()


@router.post("/register", response_model=schemas.Token, tags=["auth"], status_code=status.HTTP_201_CREATED)
async def process_register(
    request: Request,
    form_data: schemas.OAuth2PasswordRequestFormUpdate = Depends(),
    db: Session = Depends(get_db)
    ):
    email = form_data.username
    if not is_email_valid(email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid username",
        )
    user = get_user(db, form_data.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="An account with this email already exists!"
        )
    
    form_data.password = get_password_hash(form_data.password)
    user = models.User(
        email=form_data.username,
        password=form_data.password,
        first_name=form_data.first_name.capitalize(),
        last_name=form_data.last_name.capitalize(),
    )
    db_user = create_user(db, user)

    token_data = {"sub": db_user.email}

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(token_data, expires_delta=access_token_expires)

    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_refresh_token(token_data, expires_delta=refresh_token_expires)
    create_user_refresh_token(db, db_user.id, refresh_token)

    white_ip = request.client.host  # type: ignore
    create_user_white_ip(db, db_user.id, white_ip)
    
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}