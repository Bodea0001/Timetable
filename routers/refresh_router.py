from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Request, HTTPException, status

from sql.models import User
from models.schemas import Token
from crud.token import (
    has_user_refresh_token,
    delete_user_refresh_token,
    create_user_refresh_token,
)
from crud.ip import has_user_white_ip
from controllers.db import get_db
from controllers.oauth2 import oauth2_scheme
from controllers.user import get_current_user
from controllers.token import create_access_and_refresh_tokens
from message import UNKNOWN_REFRESH_TOKEN, UNKNOWN_USER_WHITE_IP


router = APIRouter()


@router.post("/refresh", tags=["auth"], response_model=Token)
async def refresh_tokens(
    request: Request,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
    user: User = Depends(get_current_user),
):
    white_ip = request.client.host  # type: ignore
    if not has_user_white_ip(db, user.id, white_ip):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=UNKNOWN_USER_WHITE_IP)

    if not has_user_refresh_token(db, user.id, token):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=UNKNOWN_REFRESH_TOKEN)
    
    delete_user_refresh_token(db, user.id, token)

    token_data = {"sub": user.email}
    tokens = create_access_and_refresh_tokens(token_data)

    create_user_refresh_token(db, user.id, tokens.refresh_token)
    
    return tokens
