from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, exists, and_, func

from sql.models import UserRefreshToken


def has_user_refresh_token(
        db: Session, user_id: int | Column[Integer],
        refresh_token: str) -> bool:
    """Проверяет, был ли создан пользователю такой refresh токен"""
    return db.query(exists().where(and_(
        UserRefreshToken.id_user == user_id,
        UserRefreshToken.refresh_token == refresh_token))).scalar()


def get_amount_of_user_refresh_tokens(
        db: Session, user_id: int | Column[Integer]) -> int:
    """Отдаёт количество токенов пользователя"""
    return db.query(func.count(UserRefreshToken.refresh_token)).filter(
        UserRefreshToken.id_user == user_id).scalar()


def create_user_refresh_token(
        db: Session, user_id: int | Column[Integer], 
        refresh_token: str) -> UserRefreshToken:
    """Создаёт и возвращает refresh токен для пользователя"""
    db_user_refresh_token = UserRefreshToken(
        id_user = user_id,
        refresh_token = refresh_token
    )
    db.add(db_user_refresh_token)
    db.commit()
    db.refresh(db_user_refresh_token)
    return db_user_refresh_token


def delete_user_refresh_token(
        db: Session, user_id: int | Column[Integer], refresh_token: str):
    """Удаляет полученный refresh токен у пользователя"""
    db.query(UserRefreshToken).filter(
        UserRefreshToken.id_user == user_id,
        UserRefreshToken.refresh_token == refresh_token
    ).delete()
    db.commit()


def delete_all_user_refresh_token(db: Session, user_id: int | Column[Integer]):
    """Удаляет все refresh токены пользователя"""
    db.query(UserRefreshToken).filter(
        UserRefreshToken.id_user == user_id
    ).delete()
    db.commit()
