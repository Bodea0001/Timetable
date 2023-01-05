from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status

from sql import models
from sql.crud import update_user, is_user_tg
from models import schemas
from controllers.db import get_db
from controllers.user import get_current_user, get_valid_user

router = APIRouter(
    prefix="/user",
    tags=["user"]
)


@router.get(
    path="/get_info",
    response_model=schemas.UserOut,
    summary="Get information about user",
    description="Get information about user by access token",
)
async def read_user(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return get_valid_user(db, user)

@router.patch(
    path="/update",
    response_model=schemas.UserOut,
    summary="Update first_name, last_name, tg_username",
)
async def update_user_information(
    first_name: str,
    last_name: str,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    user_data = schemas.UserUpdate(
        first_name=first_name.capitalize(),
        last_name=last_name.capitalize(),
    )
    update_user(db, user.id, user_data)
    return get_valid_user(db, user)