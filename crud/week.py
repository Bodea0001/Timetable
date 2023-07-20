from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer

from sql import models
from models import schemas


def create_upper_weekly_timetable(
    db: Session, 
    timetable_id: int | Column[Integer], 
    upper_weekly_timetable: list[schemas.WeekCreate]
):
    """Создаёт расписание верхней недели"""
    for upper_daily_timetable in upper_weekly_timetable:
        create_upper_week_day(db, timetable_id, upper_daily_timetable)
    

def create_upper_week_day(
    db: Session, 
    timetable_id: int | Column[Integer], 
    upper_daily_timetable: schemas.WeekCreate
):
    """Создаёт день верхней недели и расписание для него"""
    upper_day = _create_day_in_upper_week(db, timetable_id, upper_daily_timetable.day)
    for upper_day_subject in upper_daily_timetable.subjects:
        create_upper_day_subject(db, upper_day.id, upper_day_subject)


def _create_day_in_upper_week(
    db: Session, 
    timetable_id: int | Column[Integer], 
    day: schemas.Day
) -> models.UpperWeek:
    """Создаёт день верхней недели"""
    db_upper_week = models.UpperWeek(id_timetable = timetable_id, day = day)
    db.add(db_upper_week)
    db.commit()
    db.refresh(db_upper_week)
    return db_upper_week


def create_upper_day_subject(
    db: Session,
    upper_day_id: int | Column[Integer],
    upper_day_subject: schemas.DaySubjectsBase
):
    """Создаёт предмет в расписании дня верхней недели"""
    db_upper_day_subject = models.UpperDaySubjects(
        id_upper_week = upper_day_id,
        subject = upper_day_subject.subject,
        start_time = upper_day_subject.start_time,
        end_time = upper_day_subject.end_time
    )
    db.add(db_upper_day_subject)
    db.commit()


def update_upper_weekly_timetable(
    db: Session, 
    upper_weekly_timetable: list[schemas.WeekUpdate]
):
    """Обновляет расписание верхней недели"""
    for upper_day_timetable in upper_weekly_timetable:
        _update_day_in_upper_week(db, upper_day_timetable.day, upper_day_timetable.id)
        for upper_day_subject in upper_day_timetable.subjects:
            _update_upper_day_subject(db, upper_day_subject)


def _update_day_in_upper_week(
    db: Session, 
    day: schemas.Day, 
    day_id: int | Column[Integer]
):
    """Обновляет название дня на верхней неделе"""
    db.query(models.UpperWeek).filter(models.UpperWeek.id == day_id).update(
        {
            models.UpperWeek.day: day
        },
        synchronize_session=False
    )
    db.commit()


def _update_upper_day_subject(
    db: Session,
    upper_day_subject: schemas.DaySubjects
):
    """Обновляет предмет в расписании дня на верхней неделе"""
    db.query(models.UpperDaySubjects).filter(
        models.UpperDaySubjects.id == upper_day_subject.id
    ).update(
        {
            models.UpperDaySubjects.subject: upper_day_subject.subject,
            models.UpperDaySubjects.start_time: upper_day_subject.start_time,
            models.UpperDaySubjects.end_time: upper_day_subject.end_time
        },
        synchronize_session=False
    )
    db.commit()


def delete_upper_weekly_timetable(
    db: Session, 
    timetable_id: int | Column[Integer]
):
    """Удаляет расписание верхней недели"""
    db.query(models.UpperWeek).filter(
        models.UpperWeek.id_timetable == timetable_id).delete()
    db.commit()


def delete_upper_daily_timetable(db: Session, day_id: int | Column[Integer]):
    """Удаляет день верхней недели и его расписание"""
    db.query(models.UpperWeek).filter(models.UpperWeek.id == day_id).delete()
    db.commit()


def delete_upper_day_subject(db: Session, subject_id: int | Column[Integer]):
    """Удаляет предмет в расписании дня на верхней неделе"""
    db.query(models.UpperDaySubjects).filter(
        models.UpperDaySubjects.id == subject_id).delete()
    db.commit()


def create_lower_weekly_timetable(
    db: Session, 
    timetable_id: int | Column[Integer], 
    lower_weekly_timetable: list[schemas.WeekCreate]
):
    """Создаёт расписание нижней недели"""
    for lower_daily_timetable in lower_weekly_timetable:
        create_lower_week_day(db, timetable_id, lower_daily_timetable)
    

def create_lower_week_day(
    db: Session, 
    timetable_id: int | Column[Integer], 
    lower_daily_timetable: schemas.WeekCreate
):
    """Создаёт день нижней недели и расписание для него"""
    lower_day = _create_day_in_lower_week(db, timetable_id, lower_daily_timetable.day)
    for lower_day_subject in lower_daily_timetable.subjects:
        create_lower_day_subject(db, lower_day.id, lower_day_subject)


def _create_day_in_lower_week(
    db: Session, 
    timetable_id: int | Column[Integer], 
    day: schemas.Day
) -> models.LowerWeek:
    """Создаёт день нижней недели"""
    db_lower_week = models.LowerWeek(id_timetable = timetable_id, day = day)
    db.add(db_lower_week)
    db.commit()
    db.refresh(db_lower_week)
    return db_lower_week


def create_lower_day_subject(
    db: Session,
    lower_day_id: int | Column[Integer],
    lower_day_subject: schemas.DaySubjectsBase
) -> models.UpperDaySubjects:
    """Создаёт предмет в расписании дня нижней недели"""
    db_lower_day_subject = models.LowerDaySubjects(
        id_lower_week = lower_day_id,
        subject = lower_day_subject.subject,
        start_time = lower_day_subject.start_time,
        end_time = lower_day_subject.end_time
    )
    db.add(db_lower_day_subject)
    db.commit()
    db.refresh(db_lower_day_subject)
    return db_lower_day_subject


def update_lower_weekly_timetable(
    db: Session, 
    lower_weekly_timetable: list[schemas.WeekUpdate]
):
    """Обновляет расписание нижней недели"""
    for lower_day_timetable in lower_weekly_timetable:
        _update_day_in_lower_week(db, lower_day_timetable.day, lower_day_timetable.id)
        for lower_day_subject in lower_day_timetable.subjects:
            _update_lower_day_subject(db, lower_day_subject)


def _update_day_in_lower_week(
    db: Session, 
    day: schemas.Day, 
    day_id: int | Column[Integer]
):
    """Обновляет название дня на нижней неделе"""
    db.query(models.LowerWeek).filter(models.LowerWeek.id == day_id).update(
        {
            models.LowerWeek.day: day
        },
        synchronize_session=False
    )
    db.commit()


def _update_lower_day_subject(
    db: Session,
    lower_day_subject: schemas.DaySubjects
):
    """Обновляет предмет в расписании дня на нижней неделе"""
    db.query(models.LowerDaySubjects).filter(
        models.LowerDaySubjects.id == lower_day_subject.id
    ).update(
        {
            models.LowerDaySubjects.subject: lower_day_subject.subject,
            models.LowerDaySubjects.start_time: lower_day_subject.start_time,
            models.LowerDaySubjects.end_time: lower_day_subject.end_time
        },
        synchronize_session=False
    )
    db.commit()


def delete_lower_weekly_timetable(
    db: Session, 
    timetable_id: int | Column[Integer]
):
    """Удаляет расписание нижней недели"""
    db.query(models.LowerWeek).filter(
        models.LowerWeek.id_timetable == timetable_id).delete()
    db.commit()


def delete_lower_daily_timetable(db: Session, day_id: int | Column[Integer]):
    """Удаляет день нижней недели и его расписание"""
    db.query(models.LowerWeek).filter(models.LowerWeek.id == day_id).delete()
    db.commit()


def delete_lower_day_subject(db: Session, subject_id: int | Column[Integer]):
    """Удаляет предмет в расписании дня на нижней неделе"""
    db.query(models.LowerDaySubjects).filter(
        models.LowerDaySubjects.id == subject_id).delete()
    db.commit()
