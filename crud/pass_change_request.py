from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer

from sql import models


def create_password_change_request(db: Session, email: str, new_password: str):
    """Создаёт в БД запрос на смену пароля"""
    password_change_request = models.PassChangeRequest(
        email = email,
        new_password = new_password
    )
    db.add(password_change_request)
    db.commit()
    db.refresh(password_change_request)
    return password_change_request


def get_password_change_request_by_id(
    db: Session, 
    id: int | Column[Integer]
) -> models.PassChangeRequest | None:
    """Отдает данные запроса по смене пароля"""
    return db.query(models.PassChangeRequest).filter(
        models.PassChangeRequest.id == id
    ).first()


def delete_password_change_request(db: Session, id: int | Column[Integer]):
    """Удаляет запрос на смену пароля"""
    db.query(models.PassChangeRequest).filter(
        models.PassChangeRequest.id == id
    ).delete()
