from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, exists, and_

from sql import models
from models import schemas


def exists_timetable(db: Session, timetable_id: int | Column[Integer]) -> bool:
    """Проверяет, есть ли расписание с данным ID"""
    return db.query(exists().where(models.Timetable.id == timetable_id)).scalar()


def exists_timetable_with_user_id_and_name(
        db: Session, name: str, user_id: int | Column[Integer]) -> bool:
    """Проверяет, есть ли расписание у пользователя с данным наименованием"""
    return db.query(exists().where(and_(
        models.TimetableUser.id_user==user_id, 
        models.Timetable.name == name))).scalar()


def exists_timetable_with_timetable_data(
        db: Session, data: schemas.TimetableCreate) -> bool:
    """Проверяет, существует ли расписание с такими данными"""
    return db.query(exists().where(and_(
        models.Timetable.name == data.name,
        models.Timetable.id_university == data.id_university,
        models.Timetable.id_specialization == data.id_specialization,
        models.Timetable.course == data.course))).scalar()


def get_timetables(
        db: Session, data: schemas.TimetableSearch, skip: int, size: int,
    ) -> list[models.Timetable] | None:
    """Находит в БД расписания, удовлетворяющие условиям и отдает список из
    расписаний, если такие расписания нашлись"""
    dct = {
        0: models.Timetable.id_university,
        1: models.Timetable.id_specialization,
        2: models.Timetable.course
    }
    args = (data.id_university, data.id_specialization, data.course)
    lst = [dct[i] == arg for i, arg in enumerate(args) if arg]
    if data.name:
        lst.append(models.Timetable.name.ilike(f"%{data.name}%"))

    return db.query(models.Timetable).filter(and_(*lst)).order_by(
        models.Timetable.name).offset(skip).limit(size).all()


def get_timetable_by_id(
        db: Session, timetable_id: int | Column[Integer]
    ) -> models.Timetable | None:
    """Находит и отдает расписание по его id"""
    return db.query(models.Timetable).filter(
        models.Timetable.id == timetable_id
    ).first()


def get_timetables_id_where_user_is_elder(
        db: Session, user_id: int | Column[Integer]
    ) -> list[int] | None:
    """Отдаёт id расписаний, где пользователь является старостой"""
    timetables_id = db.query(models.TimetableUser.id_timetable).filter(
        models.TimetableUser.id_user == user_id,
        models.TimetableUser.status == schemas.TimetableUserStatuses.elder,
    ).all()
    return [timetable_id[0] for timetable_id in timetables_id]


def create_timetable(
        db: Session, timetable: schemas.TimetableCreate
    ) -> models.Timetable:
    """Создаёт расписание в БД и отдаёт его"""
    db_timetable = models.Timetable(
        name = timetable.name,
        id_university = timetable.id_university,
        id_specialization = timetable.id_specialization,
        course = timetable.course,
    )
    db.add(db_timetable)
    db.commit()
    db.refresh(db_timetable)
    return db_timetable


def update_timetable_data(
        db: Session, 
        timetable_id: int | Column[Integer], 
        timetable_data: schemas.TimetableCreate):
    """Обновляет данные о расписании"""
    db.query(models.Timetable).filter(
        models.Timetable.id == timetable_id
    ).update(
        {
            models.Timetable.name: timetable_data.name,
            models.Timetable.id_university: timetable_data.id_university,
            models.Timetable.id_specialization: timetable_data.id_specialization,
            models.Timetable.course: timetable_data.course
        },
        synchronize_session=False
        )
    db.commit()  


def delete_timetable(db: Session, timetable_id: int | Column[Integer]):
    """Удаляет расписание из БД"""
    db.query(models.Timetable).filter(
        models.Timetable.id == timetable_id
        ).delete()
    db.commit()
