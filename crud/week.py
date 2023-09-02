from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, exists, and_

from sql import models
from models import schemas


def exists_upper_weekly_timetable(db: Session, timetable_id: int) -> bool:
    """Проверяет, существует ли верхне-недельное расписание"""
    return db.query(exists().where(
        models.UpperWeek.id_timetable == timetable_id)).scalar()


def exists_day_in_upper_weekly_timetable(
        db: Session, timetable_id: int, day: schemas.Day) -> bool:
    """Проверяет, существует ли такой день (по названию дня) 
    в верхне-недельном расписании"""
    return db.query(exists().where(and_(
        models.UpperWeek.id_timetable == timetable_id,
        models.UpperWeek.day == day))).scalar()


def exists_day_in_upper_weekly_timetable_with_id(
        db: Session, day_id: int, timetable_id: int) -> bool:
    """Проверяет, существует ли такой день (по ID) 
    в верхне-недельном расписании"""
    return db.query(exists().where(and_(
        models.UpperWeek.id == day_id,
        models.UpperWeek.id_timetable == timetable_id))).scalar()


def exists_subject_in_upper_week(
        db: Session, timetable_id: int, subject_id: int) -> bool:
    """Проверяет, существует ли предмет на верхней неделе"""
    subquery = db.query(models.UpperWeek.id).filter(
        models.UpperWeek.id_timetable == timetable_id).all()

    day_ids = [day_id[0] for day_id in subquery]

    return db.query(exists().where(and_(
        models.UpperDaySubjects.id == subject_id,
        models.UpperDaySubjects.id_upper_week.in_(day_ids)))).scalar()


def get_upper_weekly_timetable(
        db: Session, timetable_id: int) -> list[models.UpperWeek]:
    """Ищет и отдаёт верхне-недельное расписание"""
    return db.query(models.UpperWeek).filter(
        models.UpperWeek.id_timetable == timetable_id).all()


def get_day_in_upper_weekly_timetable_by_id(
        db: Session, id: int) -> schemas.UpperWeek | None:
    """Ищет и отдаёт верхне-дневное расписание по ID"""
    return db.query(models.UpperWeek).filter(models.UpperWeek.id == id).first()


def get_day_ids_in_upper_weekly_timetable(
        db: Session, timetable_id: int) -> list[int]:
    """Ищет и отдает id дней верхне-недельного расписания"""
    day_ids = db.query(models.UpperWeek.id).filter(
        models.UpperWeek.id_timetable == timetable_id).all()
    return [day_id[0] for day_id in day_ids]


def get_subject_ids_in_upper_daily_timetable(
        db: Session, day_id: int) -> list[int]:
    """Ищет и отдает id предметов верхне-дневного расписания"""
    subject_ids = db.query(models.UpperDaySubjects.id).filter(
        models.UpperDaySubjects.id_upper_week == day_id).all()
    return [subject_id[0] for subject_id in subject_ids]


def create_upper_weekly_timetable(
    db: Session, 
    timetable_id: int | Column[Integer], 
    upper_weekly_timetable: list[schemas.DayCreate]
):
    """Создаёт расписание верхней недели"""
    for upper_daily_timetable in upper_weekly_timetable:
        create_upper_week_day(db, timetable_id, upper_daily_timetable)
    

def create_upper_week_day(
    db: Session, 
    timetable_id: int | Column[Integer], 
    upper_daily_timetable: schemas.DayCreate
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
    upper_weekly_timetable: list[schemas.DayUpdate]
):
    """Обновляет расписание верхней недели"""
    for upper_day_timetable in upper_weekly_timetable:
        for upper_day_subject in upper_day_timetable.subjects:
            _update_upper_day_subject(db, upper_day_subject)


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


def exists_lower_weekly_timetable(db: Session, timetable_id: int) -> bool:
    """Проверяет, существует ли нижне-недельное расписание"""
    return db.query(exists().where(
        models.LowerWeek.id_timetable == timetable_id)).scalar()


def exists_day_in_lower_weekly_timetable(
        db: Session, timetable_id: int, day: schemas.Day) -> bool:
    """Проверяет, существует ли такой день в нижне-недельном расписании"""
    return db.query(exists().where(and_(
        models.LowerWeek.id_timetable == timetable_id,
        models.LowerWeek.day == day))).scalar()


def exists_day_in_lower_weekly_timetable_with_id(
        db: Session, day_id: int, timetable_id: int) -> bool:
    """Проверяет, существует ли такой день (по ID) 
    в нижне-недельном расписании"""
    return db.query(exists().where(and_(
        models.LowerWeek.id == day_id,
        models.LowerWeek.id_timetable == timetable_id))).scalar()


def exists_subject_in_lower_week(
        db: Session, timetable_id: int, subject_id: int) -> bool:
    """Проверяет, существует ли предмет на нижней неделе"""
    subquery = db.query(models.LowerWeek.id).filter(
        models.LowerWeek.id_timetable == timetable_id).all()

    day_ids = [day_id[0] for day_id in subquery]

    return db.query(exists().where(and_(
        models.LowerDaySubjects.id == subject_id,
        models.LowerDaySubjects.id_lower_week.in_(day_ids)))).scalar()


def get_lower_weekly_timetable(
        db: Session, timetable_id: int) -> list[models.LowerWeek]:
    """Ищет и отдаёт нижне-недельное расписание"""
    return db.query(models.LowerWeek).filter(
        models.LowerWeek.id_timetable == timetable_id).all()


def get_day_in_lower_weekly_timetable_by_id(
        db: Session, id: int) -> models.LowerWeek | None:
    """Ищет и отдаёт нижне-дневное расписание по ID"""
    return db.query(models.LowerWeek).filter(models.LowerWeek.id == id).first()


def get_day_ids_in_lower_weekly_timetable(
    db: Session, timetable_id: int) -> list[int]:
    """Ищет и отдает id дней нижне-недельного расписания"""
    day_ids = db.query(models.LowerWeek.id).filter(
        models.LowerWeek.id_timetable == timetable_id).all()
    return [day_id[0] for day_id in day_ids]


def get_subject_ids_in_lower_daily_timetable(
        db: Session, day_id: int) -> list[int]:
    """Ищет и отдает id предметов нижне-дневного расписания"""
    subject_ids = db.query(models.LowerDaySubjects.id).filter(
        models.LowerDaySubjects.id_lower_week == day_id).all()
    return [subject_id[0] for subject_id in subject_ids]


def create_lower_weekly_timetable(
    db: Session, 
    timetable_id: int | Column[Integer], 
    lower_weekly_timetable: list[schemas.DayCreate]
):
    """Создаёт расписание нижней недели"""
    for lower_daily_timetable in lower_weekly_timetable:
        create_lower_week_day(db, timetable_id, lower_daily_timetable)
    

def create_lower_week_day(
    db: Session, 
    timetable_id: int | Column[Integer], 
    lower_daily_timetable: schemas.DayCreate
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
    lower_weekly_timetable: list[schemas.DayUpdate]
):
    """Обновляет расписание нижней недели"""
    for lower_day_timetable in lower_weekly_timetable:
        for lower_day_subject in lower_day_timetable.subjects:
            _update_lower_day_subject(db, lower_day_subject)


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
