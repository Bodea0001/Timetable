from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from sql import models
from models import schemas
from controllers.db import get_db
from controllers.user import get_current_user
from controllers.timetable import get_current_timetable, get_valid_timetable

router = APIRouter()


@router.get(
    path="/users/me",
    response_model=schemas.UserOutLite,
    summary="Get information about user",
    description="Get information about user by access token",
    tags=["user", "timetable"]
    )
async def read_user(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    db_timetables = user.timetables_info
    timetables = [get_valid_timetable(db, db_timetable) for db_timetable in db_timetables]  # type: ignore
    return schemas.UserOutLite(
        id=user.id, # type: ignore
        email=user.email, # type: ignore 
        first_name=user.first_name, # type: ignore
        last_name=user.last_name, # type: ignore
        timetables_info=timetables  # type: ignore
    )
    