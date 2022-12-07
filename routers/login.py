from datetime import timedelta
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from models.schemas import Token
from controllers.user import authenticate_user
from controllers.token import create_access_token
from controllers.db import get_db
from config import ACCESS_TOKEN_EXPIRE_MINUTES


router = APIRouter()


@router.post("/login", tags=["login"], response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.email,
            },
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}