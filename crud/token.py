from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String

from sql import models


def create_user_refresh_token(
    db: Session, 
    user_id: int | Column[Integer], 
    refresh_token: str | Column[String]
) -> models.UserRefreshToken:
    """Создаёт и возвращает refresh токен для пользователя"""
    db_user_refresh_token = models.UserRefreshToken(
        id_user = user_id,
        refresh_token = refresh_token
    )
    db.add(db_user_refresh_token)
    db.commit()
    db.refresh(db_user_refresh_token)
    return db_user_refresh_token


def delete_user_refresh_token(
    db: Session, 
    user_id: int | Column[Integer], 
    refresh_token: str | Column[String]
):
    """Удаляет полученный refresh токен у пользователя"""
    db.query(models.UserRefreshToken).filter(
        models.UserRefreshToken.id_user == user_id,
        models.UserRefreshToken.refresh_token == refresh_token
        ).delete()
    db.commit()


def delete_all_user_refresh_token(db: Session, user_id: int | Column[Integer]):
    """Удаляет все refresh токены пользователя"""
    db.query(models.UserRefreshToken).filter(
        models.UserRefreshToken.id_user == user_id
    ).delete()
    db.commit()
