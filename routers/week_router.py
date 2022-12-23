from datetime import time
from sqlalchemy.orm import Session
from fastapi import APIRouter, status, Depends, Form, HTTPException

from models import schemas
from sql import models
from sql.crud import create_upper_weekly_timetable, create_lower_weekly_timetable
from controllers.db import get_db
from controllers.user import get_current_user
from controllers.week import check_days, check_time
from controllers.timetable import check_timetable


router = APIRouter(
    prefix="/week",
    tags=["week", "timetable"],
    )


@router.post(
    path="/create",
    status_code=status.HTTP_201_CREATED,
    # response_model=schemas.TimetableOut,
    summary="Create a weekly timetable",
    )
async def create_weekly_timetable(
    timetable_id: int,
    upper_weekly_timetable: list[schemas.WeekCreate],
    lower_weekly_timetable: list[schemas.WeekCreate],
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
    ):
    check_timetable(user, timetable_id)

    check_days([day_timetable.day for day_timetable in upper_weekly_timetable])

    check_days([day_timetable.day for day_timetable in lower_weekly_timetable])
    
    for day_timetable in upper_weekly_timetable:
        start_time_list = [subject.start_time for subject in day_timetable.subjects]
        end_time_list = [subject.end_time for subject in day_timetable.subjects]
        check_time(start_time_list, end_time_list)
    
    for day_timetable in lower_weekly_timetable:
        start_time_list = [subject.start_time for subject in day_timetable.subjects]
        end_time_list = [subject.end_time for subject in day_timetable.subjects]
        check_time(start_time_list, end_time_list)

    create_upper_weekly_timetable(db, timetable_id, upper_weekly_timetable)

    create_lower_weekly_timetable(db, timetable_id, lower_weekly_timetable)    