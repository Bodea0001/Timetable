from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from models import schemas
from controllers.db import get_db
from controllers.user import get_user
from controllers.token import get_token
from controllers.email import is_email_valid
from controllers.password import get_password_hash
from sql.crud import create_user
from sql import models


router = APIRouter()


@router.post("/register", response_model=schemas.UserOut ,tags=["register"], status_code=status.HTTP_201_CREATED)
async def process_register(form_data: schemas.OAuth2PasswordRequestFormUpdate = Depends(), db: Session = Depends(get_db)):
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
    return schemas.UserOut(
        id=db_user.id, # type: ignore
        email=db_user.email, # type: ignore
        first_name=db_user.first_name, # type: ignore
        last_name=db_user.last_name, # type: ignore
    )