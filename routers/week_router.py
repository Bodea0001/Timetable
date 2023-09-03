from sqlalchemy.orm import Session
from fastapi import APIRouter, status, Depends, HTTPException, Path

from models import schemas
from sql import models
from crud.timetable_user import (
    exists_timetable_user_relation,
    have_user_enough_rights_in_timetable
)
from crud.timetable import get_timetable_by_id
from controllers.db import get_db
from controllers.week import (
    delete_subject_in_db,
    exists_duplicate_ids,
    exists_duplicate_days,
    exists_weekly_timetable,
    create_day_subject_in_db,
    exists_daily_timetable_by_id,
    create_daily_timetable_in_db,
    delete_daily_timetable_in_db,
    get_day_ids_in_updating_week,
    create_weekly_timetable_in_db,
    update_weekly_timetable_in_db,
    delete_weekly_timetable_in_db,
    exists_daily_timetable_by_name,
    get_subject_ids_in_updating_week,
    exists_subject_in_weekly_timetable,
    exists_updating_day_ids_in_weekly_timetable,
    exists_updating_subject_ids_in_weekly_timetable,
)
from controllers.user import get_current_user
from controllers.timetable import get_valid_timetable
from message import (
    WEEK_NOT_FOUND,
    DUPLICATE_DAYS,
    DUPLICATE_SUBJECTS,
    DAY_ALREADY_EXISTS,
    SUBJECT_HAS_BEEN_DELETED,
    USER_DOESNT_HAVE_TIMETABLE,
    UPDATING_DAY_IDS_NOT_EXISTS,
    USER_DOESNT_HAVE_ENOUGH_RIGHTS,
    SUBJECT_NOT_FOUND_IN_TIMETABLE,
    UPDATING_SUBJECT_IDS_NOT_EXISTS,
    WEEKLY_TIMETABLE_ALREADY_EXISTS,
    DAILY_TIMETABLE_HAS_BEEN_DELETED,
    WEEKLY_TIMETABLE_HAS_BEEN_DELETED,
)


router = APIRouter(prefix="/timetable/{timetable_id}", tags=["week"])


@router.post(
    path="/week",
    summary="Создать недельное расписание",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.TimetableOut)
async def create_weekly_timetable(
    week_name: schemas.WeekName,
    weekly_timetable: list[schemas.DayCreate],
    timetable_id: int = Path(gt=0),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    if not exists_timetable_user_relation(db, user.id, timetable_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=USER_DOESNT_HAVE_TIMETABLE)

    if not have_user_enough_rights_in_timetable(db, user.id, timetable_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=USER_DOESNT_HAVE_ENOUGH_RIGHTS)

    if exists_weekly_timetable(db, week_name, timetable_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=WEEKLY_TIMETABLE_ALREADY_EXISTS)
        
    if exists_duplicate_days([day.day for day in weekly_timetable]):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=DUPLICATE_DAYS)

    create_weekly_timetable_in_db(db, week_name, timetable_id, weekly_timetable)
    
    timetable = get_timetable_by_id(db, timetable_id)
    return get_valid_timetable(db, timetable, user.id)


@router.post(
    path="/day",
    summary="Создать дневное расписание",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.TimetableOut)
async def create_daily_timetable(
    week_name: schemas.WeekName,
    daily_timetable: schemas.DayCreate,
    timetable_id: int = Path(gt=0),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    if not exists_timetable_user_relation(db, user.id, timetable_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=USER_DOESNT_HAVE_TIMETABLE)

    if not have_user_enough_rights_in_timetable(db, user.id, timetable_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=USER_DOESNT_HAVE_ENOUGH_RIGHTS)

    if exists_daily_timetable_by_name(
        db, week_name, timetable_id, daily_timetable.day):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=DAY_ALREADY_EXISTS)

    create_daily_timetable_in_db(db, week_name, timetable_id, daily_timetable)
    
    timetable = get_timetable_by_id(db, timetable_id)
    return get_valid_timetable(db, timetable, user.id)


@router.post(
    path=".day/{day_id}/subject",
    summary="Добавить предмет в дневном расписании",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.TimetableOut)
async def create_subject_in_timetable(
    week_name: schemas.WeekName,
    daily_subject: schemas.DaySubjectsBase,
    day_id: int = Path(gt=0),
    timetable_id: int = Path(gt=0),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    if not exists_timetable_user_relation(db, user.id, timetable_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=USER_DOESNT_HAVE_TIMETABLE)

    if not have_user_enough_rights_in_timetable(db, user.id, timetable_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=USER_DOESNT_HAVE_ENOUGH_RIGHTS)

    if not exists_daily_timetable_by_id(db, week_name, timetable_id, day_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=USER_DOESNT_HAVE_TIMETABLE)  

    create_day_subject_in_db(db, week_name, daily_subject, day_id)
    
    db_timetable = get_timetable_by_id(db, timetable_id)
    return get_valid_timetable(db, db_timetable, user.id)


@router.patch(
    path="/week",
    summary="Обновляет данные недельного расписания",
    status_code=status.HTTP_200_OK,
    response_model=schemas.TimetableOut)
async def update_weekly_timetable(
    week_name: schemas.WeekName,
    weekly_timetable: list[schemas.DayUpdate],
    timetable_id: int = Path(gt=0),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    if not exists_timetable_user_relation(db, user.id, timetable_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=USER_DOESNT_HAVE_TIMETABLE)

    if not have_user_enough_rights_in_timetable(db, user.id, timetable_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=USER_DOESNT_HAVE_ENOUGH_RIGHTS)

    if not exists_weekly_timetable(db, week_name, timetable_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=WEEK_NOT_FOUND)

    day_ids = get_day_ids_in_updating_week(weekly_timetable)
    if exists_duplicate_ids(day_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=DUPLICATE_DAYS)

    if not exists_updating_day_ids_in_weekly_timetable(
        db, week_name, timetable_id, day_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=UPDATING_DAY_IDS_NOT_EXISTS)
    
    subject_ids = get_subject_ids_in_updating_week(weekly_timetable)
    if exists_duplicate_ids(subject_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=DUPLICATE_SUBJECTS)        

    if not exists_updating_subject_ids_in_weekly_timetable(
        db, week_name, weekly_timetable):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=UPDATING_SUBJECT_IDS_NOT_EXISTS)

    update_weekly_timetable_in_db(db, week_name, weekly_timetable)
    
    db_timetable = get_timetable_by_id(db, timetable_id)
    return get_valid_timetable(db, db_timetable, user.id)


@router.delete(
    path="/week",
    summary="Удалить недельное расписание",
    status_code=status.HTTP_200_OK,
    response_description=WEEKLY_TIMETABLE_HAS_BEEN_DELETED)
async def delete_weekly_timetable(
    week_name: schemas.WeekName,
    timetable_id: int = Path(gt=0),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    if not exists_timetable_user_relation(db, user.id, timetable_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=USER_DOESNT_HAVE_TIMETABLE)

    if not have_user_enough_rights_in_timetable(db, user.id, timetable_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=USER_DOESNT_HAVE_ENOUGH_RIGHTS)

    if not exists_weekly_timetable(db, week_name, timetable_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=WEEKLY_TIMETABLE_ALREADY_EXISTS)
    
    delete_weekly_timetable_in_db(db, week_name, timetable_id)


@router.delete(
    path="/day/{day_id}",
    summary="Удаляет дневное расписание",
    status_code=status.HTTP_200_OK,
    response_description=DAILY_TIMETABLE_HAS_BEEN_DELETED)
async def delete_daily_timetable(
    week_name: schemas.WeekName,
    day_id: int = Path(gt=0),
    timetable_id: int = Path(gt=0),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    if not exists_timetable_user_relation(db, user.id, timetable_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=USER_DOESNT_HAVE_TIMETABLE)

    if not have_user_enough_rights_in_timetable(db, user.id, timetable_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=USER_DOESNT_HAVE_ENOUGH_RIGHTS)

    if not exists_weekly_timetable(db, week_name, timetable_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=WEEKLY_TIMETABLE_ALREADY_EXISTS)
    
    if not exists_daily_timetable_by_id(db, week_name, timetable_id, day_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=USER_DOESNT_HAVE_TIMETABLE)

    delete_daily_timetable_in_db(db, week_name, day_id)
        

@router.delete(
    path="/subject/{subject_id}",
    summary="Удалить предмет в расписании",
    status_code=status.HTTP_200_OK,
    response_description=SUBJECT_HAS_BEEN_DELETED)
async def delete_subject_in_timetable(
    week_name: schemas.WeekName,
    subject_id: int = Path(gt=0),
    timetable_id: int = Path(gt=0),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    if not exists_timetable_user_relation(db, user.id, timetable_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=USER_DOESNT_HAVE_TIMETABLE)

    if not have_user_enough_rights_in_timetable(db, user.id, timetable_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=USER_DOESNT_HAVE_ENOUGH_RIGHTS)

    if not exists_weekly_timetable(db, week_name, timetable_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=WEEKLY_TIMETABLE_ALREADY_EXISTS)
    
    if not exists_subject_in_weekly_timetable(
        db, week_name, timetable_id, subject_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=SUBJECT_NOT_FOUND_IN_TIMETABLE)

    delete_subject_in_db(db, week_name, subject_id)
