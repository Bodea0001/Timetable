from datetime import time 
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from sql import models
from models import schemas
from crud.week import (
    create_upper_week_day,
    create_lower_week_day,
    create_upper_day_subject,
    create_lower_day_subject,
    delete_upper_day_subject,
    delete_lower_day_subject,
    exists_subject_in_upper_week,
    exists_subject_in_lower_week,
    delete_upper_daily_timetable,
    delete_lower_daily_timetable,
    create_upper_weekly_timetable,
    create_lower_weekly_timetable,
    exists_upper_weekly_timetable, 
    exists_lower_weekly_timetable,
    update_upper_weekly_timetable,
    update_lower_weekly_timetable,
    delete_upper_weekly_timetable,
    delete_lower_weekly_timetable,
    exists_day_in_upper_weekly_timetable,
    exists_day_in_lower_weekly_timetable,
    get_day_ids_in_lower_weekly_timetable,
    get_day_ids_in_upper_weekly_timetable,
    get_day_in_upper_weekly_timetable_by_id,
    get_day_in_lower_weekly_timetable_by_id,
    get_subject_ids_in_lower_daily_timetable,
    get_subject_ids_in_upper_daily_timetable,
    exists_day_in_upper_weekly_timetable_with_id,
    exists_day_in_lower_weekly_timetable_with_id
)
from message import NO_TIME_ENTERED, INCORRECT_TIME


def create_weekly_timetable_in_db(
        db: Session, week_name: schemas.WeekName, timetable_id: int,
        weekly_timetable: list[schemas.DayCreate]):
    """Создаёт недельное расписание"""
    for item in weekly_timetable:
        item.subjects.sort(key=lambda value: value.start_time)
    
    for day_timetable in weekly_timetable:
        start_time_list = [subject.start_time for subject in day_timetable.subjects]
        end_time_list = [subject.end_time for subject in day_timetable.subjects]
        _check_time(start_time_list, end_time_list)

    match week_name:
        case schemas.WeekName.UPPER:
            create_upper_weekly_timetable(db, timetable_id, weekly_timetable)
        case schemas.WeekName.LOWER:
            create_lower_weekly_timetable(db, timetable_id, weekly_timetable)    


def create_daily_timetable_in_db(
        db: Session, week_name: schemas.WeekName, timetable_id: int,
        daily_timetable: schemas.DayCreate):
    """Создаёт дневное расписание"""
    daily_timetable.subjects.sort(key=lambda value: value.start_time)

    start_time_list = [subject.start_time for subject in daily_timetable.subjects]
    end_time_list = [subject.end_time for subject in daily_timetable.subjects]

    _check_time(start_time_list, end_time_list)

    match week_name:
        case schemas.WeekName.UPPER:
            create_upper_week_day(db, timetable_id, daily_timetable)
        case schemas.WeekName.LOWER:
            create_lower_week_day(db, timetable_id, daily_timetable)


def create_day_subject_in_db(
        db: Session,     week_name: schemas.WeekName,
        daily_subject: schemas.DaySubjectsBase, day_id: int):
    """Создаёт предмет в дневном расписании"""
    day = _get_daily_timetable_by_id(db, week_name, day_id)

    day.subjects.sort(key=lambda value: value.start_time)  # type: ignore

    start_time_list = [subject.start_time for subject in day.subjects] # type: ignore
    end_time_list = [subject.end_time for subject in day.subjects] # type: ignore

    _append_subject_time(daily_subject, start_time_list, end_time_list)
    _check_time(start_time_list, end_time_list)

    if week_name == schemas.WeekName.UPPER:
        create_upper_day_subject(db, day_id, daily_subject)
    elif week_name == schemas.WeekName.LOWER:
        create_lower_day_subject(db, day_id, daily_subject)


def update_weekly_timetable_in_db(
        db: Session, week_name: schemas.WeekName, 
        weekly_timetable: list[schemas.DayUpdate]):
    """Обновляет недельное расписание"""
    for item in weekly_timetable:
        item.subjects.sort(key=lambda value: value.start_time)

    for day_timetable in weekly_timetable:
        start_time_list = [subject.start_time for subject in day_timetable.subjects]
        end_time_list = [subject.end_time for subject in day_timetable.subjects]
        _check_time(start_time_list, end_time_list)

    match week_name:
        case schemas.WeekName.UPPER:
            update_upper_weekly_timetable(db, weekly_timetable)
        case schemas.WeekName.LOWER:
            update_lower_weekly_timetable(db, weekly_timetable)


def delete_weekly_timetable_in_db(
        db: Session, week_name: schemas.WeekName, timetable_id: int):
    """Удаляет недельное расписание"""
    match week_name:
        case schemas.WeekName.UPPER:
            delete_upper_weekly_timetable(db, timetable_id)
        case schemas.WeekName.LOWER:
            delete_lower_weekly_timetable(db, timetable_id)


def delete_daily_timetable_in_db(
        db: Session, week_name: schemas.WeekName, day_id: int):
    """Удаляет дневное расписание"""
    match week_name:
        case schemas.WeekName.UPPER:
            delete_upper_daily_timetable(db, day_id)
        case schemas.WeekName.LOWER:
            delete_lower_daily_timetable(db, day_id)


def delete_subject_in_db(
        db: Session, week_name: schemas.WeekName, subject_id: int):
    """Удаляет предмет"""
    match week_name:
        case schemas.WeekName.UPPER:
            delete_upper_day_subject(db, subject_id)
        case schemas.WeekName.LOWER:
            delete_lower_day_subject(db, subject_id)


def exists_weekly_timetable(
        db: Session, week_name: schemas.WeekName, timetable_id: int) -> bool:
    """Проверяет, существует ли недельное расписание"""
    match week_name:
        case schemas.WeekName.UPPER:
            return exists_upper_weekly_timetable(db, timetable_id)
        case schemas.WeekName.LOWER:
            return exists_lower_weekly_timetable(db, timetable_id)


def exists_daily_timetable_by_name(
        db: Session, week_name: schemas.WeekName,
        timetable_id: int, day: schemas.Day) -> bool:
    """Проверяет, существует ли дневное расписание по наименованию дня"""
    match week_name:
        case schemas.WeekName.UPPER:
            return exists_day_in_upper_weekly_timetable(db, timetable_id, day)
        case schemas.WeekName.LOWER:
            return exists_day_in_lower_weekly_timetable(db, timetable_id, day)


def exists_daily_timetable_by_id(
        db: Session, week_name: schemas.WeekName,
        timetable_id: int, day_id: int) -> bool:
    """Проверяет, существует ли дневное расписание по ID дня"""
    match week_name:
        case schemas.WeekName.UPPER:
            return exists_day_in_upper_weekly_timetable_with_id(
                db, timetable_id, day_id)
        case schemas.WeekName.LOWER:
            return exists_day_in_lower_weekly_timetable_with_id(
                db, timetable_id, day_id)


def exists_subject_in_weekly_timetable(
        db: Session, week_name: schemas.WeekName,
        timetable_id: int, subject_id: int) -> bool:
    """Проверяет, существует ли предмет в расписании"""
    match week_name:
        case schemas.WeekName.UPPER:
            return exists_subject_in_upper_week(db, timetable_id, subject_id)
        case schemas.WeekName.LOWER:
            return exists_subject_in_lower_week(db, timetable_id, subject_id)


def exists_updating_day_ids_in_weekly_timetable(
        db: Session, week_name: schemas.WeekName, 
        timetable_id: int, updating_day_ids: list[int]) -> bool:
    """Проверяет, входят ли id дней для обновления в недельном расписании"""
    day_ids = _get_day_ids_in_weekly_timetable(db, week_name, timetable_id)
    return set(day_ids).issuperset(updating_day_ids)


def exists_updating_subject_ids_in_weekly_timetable(
        db: Session, week_name: schemas.WeekName, week: list[schemas.DayUpdate]
    ) -> bool:
    """Проверяет, входят ли id предметов для каждого дня на обновления в 
    недельном расписании"""
    for day in week:
        subject_ids = _get_subject_ids_in_daily_timetable(db, week_name, day.id)
        updating_subject_ids = _get_subject_ids_in_updating_day(day)

        if not set(subject_ids).issuperset(updating_subject_ids):
            return False

    return True


def exists_duplicate_ids(ids: list[int]) -> bool:
    """Проверяет, есть ли дупликаты id"""
    return len(ids) != len(set(ids))


def exists_duplicate_days(days: list[schemas.Day]) -> bool:
    """Проверяет, есть ли дупликаты дней (проверяет по наименованиям дней)"""
    days_sorted = set(days)
    if len(days_sorted) != len(days):
        return True
    return False


def get_day_ids_in_updating_week(week: list[schemas.DayUpdate]) -> list[int]:
    """Отдаёт id дней в недельном расписании для обновления"""
    return [day.id for day in week]


def get_subject_ids_in_updating_week(week: list[schemas.DayUpdate]) -> list[int]:
    """Отдаёт id предметов в недельном расписании для обновления"""
    return [subject.id for day in week for subject in day.subjects]
            

def _get_day_ids_in_weekly_timetable(
        db: Session, week_name: schemas.WeekName, timetable_id: int) -> list[int]:
    """Отдает id дней недельного расписания"""
    match week_name:
        case schemas.WeekName.UPPER:
            return get_day_ids_in_upper_weekly_timetable(db, timetable_id)
        case schemas.WeekName.LOWER:
            return get_day_ids_in_lower_weekly_timetable(db, timetable_id)


def _get_subject_ids_in_daily_timetable(
        db: Session, week_name: schemas.WeekName, day_id: int) -> list[int]:
    """Отдает id дней недельного расписания"""
    match week_name:
        case schemas.WeekName.UPPER:
            return get_subject_ids_in_upper_daily_timetable(db, day_id)
        case schemas.WeekName.LOWER:
            return get_subject_ids_in_lower_daily_timetable(db, day_id)  


def _get_daily_timetable_by_id(
        db: Session, week_name: schemas.WeekName,
        day_id: int) -> schemas.UpperWeek | schemas.LowerWeek | None:
    """Проверяет, существует ли дневное расписание"""
    match week_name:
        case schemas.WeekName.UPPER:
            return get_day_in_upper_weekly_timetable_by_id(db, day_id)
        case schemas.WeekName.LOWER:
            return get_day_in_lower_weekly_timetable_by_id(db, day_id)


def _get_subject_ids_in_updating_day(day: schemas.DayUpdate) -> list[int]:
    """Отдаёт id предметов в дневном расписании для обновления"""
    return [subject.id for subject in day.subjects]


def _append_subject_time(
        daily_subject: schemas.DaySubjectsBase,
        start_time_list: list[time],
        end_time_list: list[time]):
    """Добавляет начальное и конченое время предмета в списки с начальным и 
    конечным временем"""
    if (daily_subject.start_time in start_time_list or 
        daily_subject.end_time in end_time_list):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This time is already occupied")

    for i in range(len(start_time_list)):
        if daily_subject.start_time < start_time_list[i]:
            start_time_list.insert(i, daily_subject.start_time)
            end_time_list.insert(i, daily_subject.end_time)
            break
    else:
        start_time_list.append(daily_subject.start_time)
        end_time_list.append(daily_subject.end_time)


def _check_time(start_time: list[time], end_time:list[time]):
    """Проверяет, не пересекаются ли начальное и конечное время"""
    if len(start_time) != len(end_time):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=NO_TIME_ENTERED)

    for i in range(len(start_time) - 1):
        if start_time[i+1] < end_time[i] or start_time[i] > end_time[i]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=INCORRECT_TIME)

    if start_time[-1] > end_time[-1]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=INCORRECT_TIME)


def validate_upper_week_items(
        upper_week_items: list[models.UpperWeek]) -> list[schemas.UpperWeek]:
    """Валидирует верхне-недельное расписание"""
    valid_upper_week_items = []
    for upper_day_items in upper_week_items:
        valid_upper_day_subjects = []
        for upper_day_subject in upper_day_items.subjects:  # type: ignore
            valid_upper_day_subject = _validate_upper_day_subject(upper_day_subject)
            valid_upper_day_subjects.append(valid_upper_day_subject)
        valid_upper_day_items = _validate_day_in_upper_week(
            upper_day_items, valid_upper_day_subjects)
        valid_upper_week_items.append(valid_upper_day_items)
    return valid_upper_week_items


def _validate_upper_day_subject(
        upper_day_subject: models.UpperDaySubjects) -> schemas.UpperDaySubjects:
    """Валидирует предметы в дне верхне-недельного расписания"""
    return schemas.UpperDaySubjects(
        id = upper_day_subject.id,  # type: ignore
        id_upper_week = upper_day_subject.id_upper_week,  # type: ignore
        subject=upper_day_subject.subject,  # type: ignore
        start_time=upper_day_subject.start_time,  # type: ignore
        end_time=upper_day_subject.end_time,  # type: ignore
    )


def _validate_day_in_upper_week(
        upper_day_items: models.UpperWeek,
        upper_day_subjects: list[schemas.UpperDaySubjects],
    ) -> schemas.UpperWeek:
    """Валидирует дневное расписание на верхней неделе"""
    return schemas.UpperWeek(
        id=upper_day_items.id,  # type: ignore
        id_timetable=upper_day_items.id_timetable,  # type: ignore
        day=upper_day_items.day,  # type: ignore
        subjects=upper_day_subjects
        )


def validate_lower_week_items(
        lower_week_items: list[models.LowerWeek]) -> list[schemas.LowerWeek]:
    """Валидирует нижне-недельное расписание"""
    valid_lower_week_items = []
    for lower_day_items in lower_week_items:
        valid_lower_day_subjects = []
        for lower_day_subject in lower_day_items.subjects:  # type: ignore
            valid_lower_day_subject = _validate_lower_day_subject(lower_day_subject)
            valid_lower_day_subjects.append(valid_lower_day_subject)
        valid_lower_day_items = _validate_day_in_lower_week(
            lower_day_items, valid_lower_day_subjects)
        valid_lower_week_items.append(valid_lower_day_items)
    return valid_lower_week_items


def _validate_lower_day_subject(
        lower_day_subject: models.LowerDaySubjects) -> schemas.LowerDaySubjects:
    """Валидирует предметы в дне нижне-недельного расписания"""
    return schemas.LowerDaySubjects(
        id = lower_day_subject.id,  # type: ignore
        id_lower_week = lower_day_subject.id_lower_week,  # type: ignore
        subject=lower_day_subject.subject,  # type: ignore
        start_time=lower_day_subject.start_time,  # type: ignore
        end_time=lower_day_subject.end_time,  # type: ignore
    )


def _validate_day_in_lower_week(
        lower_day_items: models.LowerWeek,
        lower_day_subjects: list[schemas.LowerDaySubjects],
    ) -> schemas.LowerWeek:
    """Валидирует дневное расписание на нижней неделе"""
    return schemas.LowerWeek(
        id=lower_day_items.id,  # type: ignore
        id_timetable=lower_day_items.id_timetable,  # type: ignore
        day=lower_day_items.day,  # type: ignore
        subjects=lower_day_subjects
        )
