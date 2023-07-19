from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Request

from sql.models import User
from models.schemas import Token
from controllers.db import get_db
from controllers.user import (
    get_current_user,
    check_user_white_ip,
    check_user_refresh_token,
    is_user_refresh_tokens_limit_exceeded
)
from controllers.oauth2 import oauth2_scheme
from controllers.token import create_access_and_refresh_tokens
from crud.token import delete_user_refresh_token, create_user_refresh_token


router = APIRouter()


@router.post("/refresh", tags=["auth"], response_model=Token)
async def refresh_tokens(
    request: Request,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
    user: User = Depends(get_current_user),
):
    white_ip = request.client.host  # type: ignore
    check_user_white_ip(white_ip, user.white_list_ip)  # type: ignore

    check_user_refresh_token(token, user.refresh_tokens)  # type: ignore
    
    if not is_user_refresh_tokens_limit_exceeded(
        db, len(user.refresh_tokens), user.id):  # type: ignore
        delete_user_refresh_token(db, user.id, token)

    token_data = {"sub": user.email}
    tokens = create_access_and_refresh_tokens(token_data)

    create_user_refresh_token(db, user.id, tokens.refresh_token)
    
    return tokens
