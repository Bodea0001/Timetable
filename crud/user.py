from sqlalchemy import Column, Integer, String, exists
from sqlalchemy.orm import Session

from sql import models
from models import schemas


def get_user(db: Session, username: str | Column[String]) -> models.User | None:
    """Отдаёт информацию о пользователе из БД по его почте, если пользователь
    с такой почтой существует. В противном случае ничего не возвращает"""
    return db.query(models.User).filter(models.User.email == username).first()


def get_public_information_about_user(
    db: Session,
    user_id: int | Column[Integer]
) -> schemas.UserPublicInformation | None:
    """Отдаёт почту, фамилию и имя пользователя из БД по его ID, если 
    пользователь с таким ID существует. В противном случае ничего не возвращает"""
    user_public_info: models.User | None =  db.query(
        models.User.email, 
        models.User.first_name, 
        models.User.last_name
    ).filter(models.User.id == user_id).first()

    if user_public_info:
        return schemas.UserPublicInformation(
            email=user_public_info.email,
            first_name=user_public_info.first_name,
            last_name=user_public_info.last_name)


def update_user(
    db: Session, 
    user_id: int | Column[Integer], 
    user_data: schemas.UserUpdate
):
    """Обновляет данные (имя и фамилию) пользователя в БД"""
    db.query(models.User).filter(models.User.id == user_id).update(
        {
            models.User.first_name: user_data.first_name,
            models.User.last_name: user_data.last_name,
        },
        synchronize_session=False
        )
    db.commit()  


def update_user_password(
    db: Session, 
    user_id: int | Column[Integer], 
    new_password: str | Column[String]
):
    """Обновляет пароль пользователя в БД"""
    db.query(models.User).filter(models.User.id == user_id).update(
        {
            models.User.password: new_password
        },
        synchronize_session=False
        )
    db.commit()  


def create_user_in_db(db: Session, user: schemas.UserCreate) -> models.User:
    """Создаёт нового пользователя в БД"""
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


def exists_user_with_email(db: Session, email: str) -> bool:
    """Проверяет, есть ли пользователь с такой почтой в БД"""
    return db.query(exists().where(models.User.email == email)).scalar()
