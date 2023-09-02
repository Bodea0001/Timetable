from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String

from sql import models


def get_university_by_id(
        db: Session, university_id: int | Column[Integer]
    ) -> models.University | None:
    return db.query(models.University).filter(
        models.University.id == university_id).first()


def get_university_id_by_name_from_db(
        db: Session, university_name: str | Column[String]
    ) -> int | None:
    """Ищет университет в БД по его имени и отдаёт"""
    return db.query(models.University.id).filter(
        models.University.name == university_name).scalar()


def get_university_by_id_from_db(
        db: Session, university_id: int | Column[Integer]
    ) -> models.University | None:
    """Ищет университет в БД по его id и отдаёт"""
    return db.query(models.University).filter(
        models.University.id == university_id).first()
