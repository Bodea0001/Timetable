from sqlalchemy import Column, Integer
from sqlalchemy.orm import Session

from sql import models
from models import schemas


def get_user(db: Session, username: str) -> models.User | None:
    return db.query(models.User).filter(models.User.email == username).first()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    db_user = models.User(
        email=user.email,
        password=user.password,
        first_name=user.first_name,
        last_name=user.last_name,
        )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_timetable(db: Session, user_id: int | Column[Integer], timetable_name: str) -> models.Timetable | None:
    return db.query(models.Timetable).filter(models.Timetable.id_user == user_id, models.Timetable.name == timetable_name).first()


def get_timetables_by_user_id(db: Session, user_id: int) -> list[models.Timetable] | None:
    return db.query(models.Timetable).filter(models.Timetable.id_user == user_id).all()


def create_timetable(db: Session, timetable: schemas.TimetableCreate) -> models.Timetable:
    db_timetable = models.Timetable(
        name = timetable.name,
        id_university = timetable.id_university,
        id_speсialization = timetable.id_specialization,
        education_level = timetable.education_level,
        course = timetable.course,
        id_user = timetable.id_user,
        status = timetable.status
    )
    db.add(db_timetable)
    db.commit()
    db.refresh(db_timetable)
    return db_timetable


def get_university(db: Session, university_name: str) -> models.University | None:
    return db.query(models.University).filter(models.University.name == university_name).first()


def get_university_by_id(db: Session, university_id: int) -> models.University | None:
    return db.query(models.University).filter(models.University.id == university_id).first()


def get_specialization_by_name(db: Session, specialization_name: str) -> models.Specialization | None:
    return db.query(models.Specialization).filter(models.Specialization.name == specialization_name).first()


def get_specialization_by_code(db: Session, specialization_code: str) -> models.Specialization | None:
    return db.query(models.Specialization).filter(models.Specialization.code == specialization_code).first()


def get_specialization_by_id(db: Session, specialization_id: int) -> models.Specialization | None:
    return db.query(models.Specialization).filter(models.Specialization.id == specialization_id).first()


def filter_timetablse(
    db: Session,
    name: str | models.Timetable,
    university_id: int | models.Timetable,
    specialization_id: int | models.Timetable,
    course: int | models.Timetable
    ) -> list[models.Timetable] | None:
    return db.query(models.Timetable).filter(
        models.Timetable.name == name,
        models.Timetable.id_university == university_id,
        models.Timetable.id_speсialization == specialization_id,
        models.Timetable.course == course
        ).all()