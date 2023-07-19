from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session

from sql import models
from models import schemas


def get_timetables(
    db: Session,
    timetable_name: str | Column[String],
    university_id: int | Column[Integer],
    specialization_id: int | Column[Integer],
    course: int | Column[Integer],
    skip: int,
    limit: int,
) -> list[models.Timetable] | None:
    """Находит в БД расписания, удовлетворяющие условиям и отдает список из
    расписаний, если такие расписания нашлись"""
    return db.query(models.Timetable).filter(
        models.Timetable.name == timetable_name,
        models.Timetable.id_university == university_id,
        models.Timetable.id_specialization == specialization_id,
        models.Timetable.course == course,
    ).offset(skip).limit(limit).all()


def get_timetable_by_name_and_user_id(
    db: Session,
    timetable_name: str | Column[String],
    user_id: int | Column[Integer],
) -> models.Timetable | None:
    """Находит расписание по названию расписания и id пользователя и отдает его"""
    return db.query(models.Timetable).join(
        models.TimetableUser,
        models.TimetableUser.id_user == user_id
    ).filter(models.Timetable.name == timetable_name).first()


def get_timetable_by_id(
    db: Session, 
    timetable_id: int | Column[Integer]
) -> models.Timetable | None:
    """Находит и отдает расписание по его id"""
    return db.query(models.Timetable).filter(
        models.Timetable.id == timetable_id
    ).first()


def get_timetable_by_name_university_id_specialization_id_course(
    db: Session,
    name: str | Column[String],
    university_id: int | Column[Integer],
    specialization_id: int | Column[Integer],
    course: int | Column[Integer],
) -> models.Timetable | None:
    """Находит расписание по его названию, университету, специальности и курсу
    и отдаёт его"""
    return db.query(models.Timetable).filter(
        models.Timetable.name == name,
        models.Timetable.id_university == university_id,
        models.Timetable.id_specialization == specialization_id,
        models.Timetable.course == course
    ).first()


def get_timetables_id_where_user_is_elder(
    db: Session, 
    user_id: int | Column[Integer]
) -> list[int] | None:
    """Отдаёт id расписаний, где пользователь является старостой"""
    timetables_id = db.query(models.TimetableUser.id_timetable).filter(
        models.TimetableUser.id_user == user_id,
        models.TimetableUser.status == schemas.TimetableUserStatuses.elder,
    ).all()
    return [timetable_id[0] for timetable_id in timetables_id]


def create_timetable(
    db: Session, 
    timetable: schemas.TimetableCreate
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


def update_timetable(
    db: Session, 
    timetable_id: int | Column[Integer], 
    timetable_data: schemas.TimetableCreate
):
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
