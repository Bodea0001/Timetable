from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String

from sql import models


def get_university(
    db: Session, 
    university_name: str | Column[String]
) -> models.University | None:
    """Ищет университет в БД по его имени и отдаёт"""
    return db.query(models.University).filter(
        models.University.name == university_name).first()


def get_university_by_id(
    db: Session,
    university_id: int | Column[Integer]
) -> models.University | None:
    """Ищет университет в БД по его id и отдаёт"""
    return db.query(models.University).filter(
        models.University.id == university_id).first()
