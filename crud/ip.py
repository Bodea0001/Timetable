from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, exists, and_

from sql.models import UserWhiteIP


def create_user_white_ip(
        db: Session, 
        user_id: int | Column[Integer], 
        white_ip: str | Column[String]
    ) -> UserWhiteIP:
    """Создает белый ip пользователя (т.е. ip, по которому 
    пользователь когда-либо логинился)"""
    db_user_white_ip = UserWhiteIP(
        id_user = user_id,
        white_ip = white_ip
    )
    db.add(db_user_white_ip)
    db.commit()
    db.refresh(db_user_white_ip)
    return db_user_white_ip


def has_user_white_ip(
        db: Session, user_id: int | Column[Integer],
        white_ip: str) -> bool:
    """Проверяет, заходил ли пользователь под данным ip"""
    return db.query(exists().where(and_(
        UserWhiteIP.id_user == user_id,
        UserWhiteIP.white_ip == white_ip))).scalar()
