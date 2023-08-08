from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String

from sql import models
from models import schemas


def get_specialization_id_by_name(
        db: Session,
        specialization_name: str | Column[String],
        education_level: schemas.Education_level) -> int | None:
    """Ищет специальность в БД по названию и уровню образования и отдаёт"""
    return db.query(models.Specialization.id).filter(
        models.Specialization.name == specialization_name,
        models.Specialization.education_level == education_level).scalar()


def get_specialization_id_by_code(
        db: Session, specialization_code: str | Column[String],
    ) -> models.Specialization | None:
    """Ищет специальность в БД по коду и отдаёт"""
    return db.query(models.Specialization.id).filter(
        models.Specialization.code == specialization_code,).scalar()


def get_specialization_by_id(
        db: Session, specialization_id: int | Column[Integer]
    ) -> models.Specialization | None:
    """Ищет специальность в БД по ID и отдаёт"""
    return db.query(models.Specialization).filter(
        models.Specialization.id == specialization_id).first()
