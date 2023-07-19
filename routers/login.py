from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, HTTPException, status, Depends, Request

from models.schemas import Token
from crud.ip import create_user_white_ip
from crud.token import create_user_refresh_token
from controllers.db import get_db
from controllers.token import create_access_and_refresh_tokens
from controllers.user import authenticate_user, is_user_refresh_tokens_limit_exceeded


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

    is_user_refresh_tokens_limit_exceeded(db, len(user.refresh_tokens), user.id)  # type: ignore

    token_data = {"sub": user.email}
    tokens = create_access_and_refresh_tokens(token_data)

    create_user_refresh_token(db, user.id, tokens.refresh_token)
    
    white_ip = request.client.host  # type: ignore
    user_white_list_ip = [value.white_ip for value in user.white_list_ip]  # type: ignore
    if white_ip not in user_white_list_ip:
        create_user_white_ip(db, user.id, white_ip)
    
    return tokens