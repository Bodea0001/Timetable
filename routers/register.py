from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status, HTTPException, Request

from crud.ip import create_user_white_ip
from crud.user import exists_user_with_email
from crud.token import create_user_refresh_token
from controllers.db import get_db
from controllers.user import create_user
from controllers.token import create_access_and_refresh_tokens
from models.schemas import Token, OAuth2PasswordRequestFormUpdate


router = APIRouter()


@router.post(
    path="/signup",
    response_model=Token,
    tags=["auth"],
    status_code=status.HTTP_201_CREATED
)
async def process_register(
    request: Request,
    form_data: OAuth2PasswordRequestFormUpdate = Depends(),
    db: Session = Depends(get_db)
):
    if exists_user_with_email(db, form_data.username):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="An account with this email already exists!")
    
    user = create_user(db, form_data)

    token_data = {"sub": user.email}
    tokens = create_access_and_refresh_tokens(token_data)

    create_user_refresh_token(db, user.id, tokens.refresh_token)

    white_ip = request.client.host  # type: ignore
    create_user_white_ip(db, user.id, white_ip)
    
    return tokens
