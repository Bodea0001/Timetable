from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, HTTPException, status, Depends, Request

from models.schemas import Token
from controllers.db import get_db
from controllers.user import (
    authenticate_user,
    is_user_refresh_tokens_limit_exceeded
)
from controllers.token import create_access_and_refresh_tokens
from crud.ip import create_user_white_ip, has_user_white_ip
from crud.token import create_user_refresh_token, delete_all_user_refresh_token


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
            headers={"WWW-Authenticate": "Bearer"})

    if is_user_refresh_tokens_limit_exceeded(db, user.id):
        delete_all_user_refresh_token(db, user.id)

    token_data = {"sub": user.email}
    tokens = create_access_and_refresh_tokens(token_data)

    create_user_refresh_token(db, user.id, tokens.refresh_token)
    
    white_ip = request.client.host  # type: ignore
    if not has_user_white_ip(db, user.id, white_ip):
        create_user_white_ip(db, user.id, white_ip)
    
    return tokens