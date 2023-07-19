from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String

from sql import models


def create_user_white_ip(
    db: Session, 
    user_id: int | Column[Integer], 
white_ip: str | Column[String]
) -> models.UserWhiteIP:
    """Создает белый ip пользователя (т.е. ip, по которому 
    пользователь когда-либо логинился)"""
    db_user_white_ip = models.UserWhiteIP(
        id_user = user_id,
        white_ip = white_ip
    )
    db.add(db_user_white_ip)
    db.commit()
    db.refresh(db_user_white_ip)
    return db_user_white_ip
