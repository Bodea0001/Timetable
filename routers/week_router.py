from datetime import time
from sqlalchemy.orm import Session
from fastapi import APIRouter, status, Depends, Form, HTTPException

from models import schemas
from sql import models
from sql.crud import (
    create_upper_weekly_timetable,
    create_lower_weekly_timetable,
    create_upper_week_day,
    create_lower_week_day,
    create_upper_day_subject,
    create_lower_day_subject,
    update_upper_weekly_timetable,
    update_lower_weekly_timetable,
    delete_upper_weekly_timetable,
    delete_upper_daily_timetable,
    delete_upper_day_subject,
    delete_lower_weekly_timetable,
    delete_lower_daily_timetable,
    delete_lower_day_subject,
    get_timetable_user_status,
    get_timetable_by_id
)
from controllers.db import get_db
from controllers.user import get_current_user
from controllers.week import (
    check_days, check_time,
    check_week_and_subject_ids,
    check_day_in_timetable,
    check_subject_id_in_timetable,
    append_subject_time
)
from controllers.timetable import check_timetable, get_valid_timetable


router = APIRouter(
    prefix="/timetable/week",
    tags=["week"],
    )


@router.post(
    path="/create_week",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.TimetableOut,
    summary="Create a weekly timetable",
)
async def create_weekly_timetable(
    timetable_id: int,
    week_name: schemas.WeekName,
    weekly_timetable: list[schemas.WeekCreate],
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    timetable = check_timetable(user, timetable_id)

    timetable_user_status = get_timetable_user_status(db, user.id, timetable_id)
    if timetable_user_status != schemas.TimetableUserStatuses.elder:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"The user doesn't have access rights to create weekly timetable"
        )

    if week_name == schemas.WeekName.UPPER and timetable.upper_week_items or \
        week_name == schemas.WeekName.LOWER and timetable.lower_week_items:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The weekly timetable already exists"
        )
        
    check_days([day_timetable.day for day_timetable in weekly_timetable])

    for item in weekly_timetable:
        item.subjects.sort(key=lambda value: value.start_time)
    
    for day_timetable in weekly_timetable:
        start_time_list = [subject.start_time for subject in day_timetable.subjects]
        end_time_list = [subject.end_time for subject in day_timetable.subjects]
        check_time(start_time_list, end_time_list)

    if week_name == schemas.WeekName.UPPER:
        create_upper_weekly_timetable(db, timetable_id, weekly_timetable)
    elif week_name == schemas.WeekName.LOWER:
        create_lower_weekly_timetable(db, timetable_id, weekly_timetable)
    
    db_timetable = get_timetable_by_id(db, timetable_id)
    return get_valid_timetable(db, db_timetable)


@router.post(
    path="/create_day",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.TimetableOut,
    summary="Create daily timetable",
)
async def create_daily_timetable(
    timetable_id: int,
    week_name: schemas.WeekName,
    daily_timetable: schemas.WeekCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    timetable = check_timetable(user, timetable_id)

    timetable_user_status = get_timetable_user_status(db, user.id, timetable_id)
    if timetable_user_status != schemas.TimetableUserStatuses.elder:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"The user doesn't have access rights to create weekly timetable"
        )

    if week_name == schemas.WeekName.UPPER and timetable.upper_week_items:
        week_days = [value.day for value in timetable.upper_week_items]
    elif week_name == schemas.WeekName.LOWER and timetable.lower_week_items:
        week_days = [value.day for value in timetable.lower_week_items]
    else:
        week_days = None   
    if week_days and daily_timetable.day in week_days:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This day already exists in the transmitted timetable"
        )

    daily_timetable.subjects.sort(key=lambda value: value.start_time)

    start_time_list = [subject.start_time for subject in daily_timetable.subjects]
    end_time_list = [subject.end_time for subject in daily_timetable.subjects]
    check_time(start_time_list, end_time_list)

    if week_name == schemas.WeekName.UPPER:
        create_upper_week_day(db, timetable_id, daily_timetable)
    elif week_name == schemas.WeekName.LOWER:
        create_lower_week_day(db, timetable_id, daily_timetable)
    
    db_timetable = get_timetable_by_id(db, timetable_id)
    return get_valid_timetable(db, db_timetable)


@router.post(
    path="/create_subject",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.TimetableOut,
    summary="Create a subject in the timetable",
)
async def create_subject_in_timetable(
    timetable_id: int,
    day_id: int,
    week_name: schemas.WeekName,
    daily_subject: schemas.DaySubjectsBase,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    timetable = check_timetable(user, timetable_id)

    timetable_user_status = get_timetable_user_status(db, user.id, timetable_id)
    if timetable_user_status != schemas.TimetableUserStatuses.elder:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"The user doesn't have access rights to create weekly timetable"
        )

    submitted_day = check_day_in_timetable(week_name, day_id, timetable)

    submitted_day.subjects.sort(key=lambda value: value.start_time)  # type: ignore
    start_time_list = [subject.start_time for subject in submitted_day.subjects]
    end_time_list = [subject.end_time for subject in submitted_day.subjects]
    append_subject_time(daily_subject, start_time_list, end_time_list)
    check_time(start_time_list, end_time_list)

    if week_name == schemas.WeekName.UPPER:
        create_upper_day_subject(db, day_id, daily_subject)
    elif week_name == schemas.WeekName.LOWER:
        create_lower_day_subject(db, day_id, daily_subject)
    
    db_timetable = get_timetable_by_id(db, timetable_id)
    return get_valid_timetable(db, db_timetable)


@router.patch(
    path="/update",
    status_code=status.HTTP_200_OK,
    response_model=schemas.TimetableOut,
    summary="Update weekly timetable",
)
async def update_weekly_timetable(
    timetable_id: int,
    week_name: schemas.WeekName,
    weekly_timetable: list[schemas.WeekUpdate],
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    timetable = check_timetable(user, timetable_id)

    timetable_user_status = get_timetable_user_status(db, user.id, timetable_id)
    if timetable_user_status != schemas.TimetableUserStatuses.elder:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"The user doesn't have access rights to create weekly timetable"
        )

    if week_name == schemas.WeekName.UPPER and not timetable.upper_week_items or \
        week_name == schemas.WeekName.LOWER and not timetable.lower_week_items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The weekly timetable doesn't exists"
        )

    if week_name == schemas.WeekName.UPPER:
        check_week_and_subject_ids(timetable.upper_week_items, weekly_timetable)
    elif week_name == schemas.WeekName.LOWER:
        check_week_and_subject_ids(timetable.lower_week_items, weekly_timetable)
 
    check_days([day_timetable.day for day_timetable in weekly_timetable])

    for item in weekly_timetable:
        item.subjects.sort(key=lambda value: value.start_time)

    for day_timetable in weekly_timetable:
        start_time_list = [subject.start_time for subject in day_timetable.subjects]
        end_time_list = [subject.end_time for subject in day_timetable.subjects]
        check_time(start_time_list, end_time_list)

    if week_name == schemas.WeekName.UPPER:
        update_upper_weekly_timetable(db, weekly_timetable)
    elif week_name == schemas.WeekName.LOWER:
        update_lower_weekly_timetable(db, weekly_timetable)
    
    db_timetable = get_timetable_by_id(db, timetable_id)
    return get_valid_timetable(db, db_timetable)


@router.delete(
    path="/delete_week",
    status_code=status.HTTP_200_OK,
    summary="Delete weekly timetable",
)
async def delete_weekly_timetable(
    timetable_id: int,
    week_name: schemas.WeekName,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    timetable = check_timetable(user, timetable_id)

    timetable_user_status = get_timetable_user_status(db, user.id, timetable_id)
    if timetable_user_status != schemas.TimetableUserStatuses.elder:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"The user doesn't have access rights to create weekly timetable"
        )

    if week_name == schemas.WeekName.UPPER and not timetable.upper_week_items or \
        week_name == schemas.WeekName.LOWER and not timetable.lower_week_items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The weekly timetable doesn't exists"
        )
    
    if week_name == schemas.WeekName.UPPER:
        delete_upper_weekly_timetable(db, timetable_id)
    elif week_name  == schemas.WeekName.LOWER:
        delete_lower_weekly_timetable(db, timetable_id)


@router.delete(
    path="/delete_day",
    status_code=status.HTTP_200_OK,
    summary="Delete daily timetable",
)
async def delete_daily_timetable(
    timetable_id: int,
    day_id: int,
    week_name: schemas.WeekName,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    timetable = check_timetable(user, timetable_id)

    timetable_user_status = get_timetable_user_status(db, user.id, timetable_id)
    if timetable_user_status != schemas.TimetableUserStatuses.elder:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"The user doesn't have access rights to create weekly timetable"
        )

    if week_name == schemas.WeekName.UPPER and not timetable.upper_week_items or \
        week_name == schemas.WeekName.LOWER and not timetable.lower_week_items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The weekly timetable doesn't exists"
        )
    
    check_day_in_timetable(week_name, day_id, timetable)

    if week_name == schemas.WeekName.UPPER:
        delete_upper_daily_timetable(db, day_id)
    elif week_name  == schemas.WeekName.LOWER:
        delete_lower_daily_timetable(db, day_id)
        

@router.delete(
    path="/delete_subject",
    status_code=status.HTTP_200_OK,
    summary="Delete subject in the timetable",
)
async def delete_subject_in_timetable(
    timetable_id: int,
    subject_id: int,
    week_name: schemas.WeekName,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    timetable = check_timetable(user, timetable_id)

    timetable_user_status = get_timetable_user_status(db, user.id, timetable_id)
    if timetable_user_status != schemas.TimetableUserStatuses.elder:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"The user doesn't have access rights to create weekly timetable"
        )

    if week_name == schemas.WeekName.UPPER and not timetable.upper_week_items or \
        week_name == schemas.WeekName.LOWER and not timetable.lower_week_items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The weekly timetable doesn't exists"
        )
    
    check_subject_id_in_timetable(week_name, subject_id, timetable)

    if week_name == schemas.WeekName.UPPER:
        delete_upper_day_subject(db, subject_id)
    elif week_name  == schemas.WeekName.LOWER:
        delete_lower_day_subject(db, subject_id)