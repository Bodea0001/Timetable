from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from sql import models
from models import schemas
from controllers.db import get_db
from controllers.user import get_current_user, validate_application
from controllers.timetable import get_current_timetable, get_valid_timetable

router = APIRouter()


@router.get(
    path="/users/me",
    tags=["user"],
    response_model=schemas.UserOut,
    summary="Get information about user",
    description="Get information about user by access token",
    )
async def read_user(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    timetables = [get_valid_timetable(db, db_timetable) for db_timetable in user.timetables_info]  # type: ignore
    applications = [validate_application(application) for application in user.applications]  # type: ignore
    return schemas.UserOut(
        id=user.id, # type: ignore
        email=user.email, # type: ignore 
        first_name=user.first_name, # type: ignore
        last_name=user.last_name, # type: ignore
        applications=applications,  # type: ignore
        timetables_info=timetables  # type: ignore
    )
    