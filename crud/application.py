from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, and_, exists

from sql import models


def create_application(
    db: Session, 
    user_id: int| Column[Integer], 
    timetable_id: int | Column[Integer]
):
    """Создаёт заявку на добавление к расписанию"""
    application = models.Application(
        id_user = user_id,
        id_timetable = timetable_id
    )
    db.add(application)
    db.commit()


def have_user_application(
    db: Session,
    user_id: int | Column[Integer],
    application_id: int | Column[Integer]
) -> bool:
    """Проверяет, подавал ли пользователь данную заявку"""
    return db.query(exists().where(and_(
        models.Application.id == application_id,
        models.Application.id_user == user_id))).scalar()


def get_application_by_id(
    db: Session, 
    application_id: int | Column[Integer]
) -> models.Application | None:
    """Ищет заявку в БД по ID и отдаёт"""
    return db.query(models.Application).filter(
        models.Application.id ==application_id).first()


def get_applications_by_timetable_id(
    db: Session, 
    timetable_id: int | Column[Integer]
) -> list[models.Application] | list[None]:
    """Ищет заявки в БД по ID расписания, к которой 
    эти заявки относятся, и отдаёт"""
    return db.query(models.Application).filter(
        models.Application.id_timetable == timetable_id).all()


def exists_application_with_user_id_and_timetable_id(
    db: Session, user_id: int | Column[Integer],
    timetable_id: int | Column[Integer]
) -> bool:
    """Проверяет, подавал ли данный пользователь заявку на 
    добавление к данному расписанию"""
    return db.query(exists().where(and_(
        models.Application.id_user == user_id,
        models.Application.id_timetable == timetable_id))).scalar()


def delete_application(db: Session, application_id: int | Column[Integer]):
    """Удаляет заявку"""
    db.query(models.Application).filter(
        models.Application.id == application_id).delete()
    db.commit()
