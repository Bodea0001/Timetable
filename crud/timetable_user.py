from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, func, exists, and_

from sql import models
from models import schemas


def create_timetable_user_relation(
    db: Session, 
    timetable_user_relation: schemas.TimetableUserCreate
):
    """Привязывает пользователя и расписание"""
    db_timetable_user_relation = models.TimetableUser(
        id_user = timetable_user_relation.id_user,
        id_timetable = timetable_user_relation.id_timetable,
        status = timetable_user_relation.status
    )
    db.add(db_timetable_user_relation)
    db.commit()


def get_timetable_user_status(
    db: Session, 
    user_id: int | Column[Integer], 
    timetable_id: int | Column[Integer]
) -> schemas.TimetableUserStatuses | None:
    """Отдаёт статус пользователя в расписании"""
    status = db.query(models.TimetableUser.status).filter(
        models.TimetableUser.id_user == user_id,
        models.TimetableUser.id_timetable == timetable_id,
        ).first()
    return status[0] if status else None


def get_timetable_elder(
    db: Session, 
    timetable_id: int | Column[Integer]
) -> int | None:
    """Отдаёт id пользователя, который в данном расписании является старостой"""
    user_id =  db.query(models.TimetableUser.id_user).filter(
        models.TimetableUser.id_timetable == timetable_id,
        models.TimetableUser.status == schemas.TimetableUserStatuses.elder
    ).first()
    return user_id[0] if user_id else None


def get_amount_of_user_timetables(
    db: Session, 
    user_id: int | Column[Integer]
) -> int:
    """Отдаёт количество расписаний пользователя"""
    return db.query(func.count(models.TimetableUser.id_timetable)).filter(
        models.TimetableUser.id_user == user_id).scalar()


def exists_timetable_user_relation(
    db: Session, 
    user_id: int | Column[Integer], 
    timetable_id: int | Column[Integer]
) -> bool:
    """Проверяет, есть ли у данного пользователя данное расписание"""
    return db.query(exists().where(and_(
        models.TimetableUser.id_user == user_id,
        models.TimetableUser.id_timetable == timetable_id
    ))).scalar()


def get_timetable_users_id(
    db: Session, 
    timetable_id: int | Column[Integer]
) -> list[int]:
    """Отдаёт id всех пользователей, прикрепленных к данному расписанию"""
    users_id = db.query(models.TimetableUser.id_user).filter(
        models.TimetableUser.id_timetable == timetable_id
    ).all()
    return [user_id[0] for user_id in users_id]


def delete_timetable_user_relation(
    db: Session, 
    user_id: int | Column[Integer], 
    timetable_id: int | Column[Integer]
):
    """Открепляет пользователя от расписания"""
    db.query(models.TimetableUser).filter(
        models.TimetableUser.id_user == user_id,
        models.TimetableUser.id_timetable == timetable_id
    ).delete()
    db.commit()
