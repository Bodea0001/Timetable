from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, func, exists, and_

from sql import models
from models.schemas import TimetableUserCreate, TimetableUserStatuses


def create_timetable_user_relation(
        db: Session, 
        timetable_user_relation: TimetableUserCreate):
    """Привязывает пользователя и расписание"""
    db_timetable_user_relation = models.TimetableUser(
        id_user = timetable_user_relation.id_user,
        id_timetable = timetable_user_relation.id_timetable,
        status = timetable_user_relation.status
    )
    db.add(db_timetable_user_relation)
    db.commit()


def get_timetable_user_status(
        db: Session, user_id: int | Column[Integer], 
        timetable_id: int | Column[Integer]) -> TimetableUserStatuses | None:
    """Отдаёт статус пользователя в расписании"""
    return db.query(models.TimetableUser.status).filter(
        models.TimetableUser.id_user == user_id,
        models.TimetableUser.id_timetable == timetable_id).scalar()


def get_user_timetables_id_by_status(
        db: Session, user_id: int | Column[Integer], 
        status: TimetableUserStatuses) -> list[int]:
    """Отдаёт расписания пользователя с данным статусом"""
    timetables_id = db.query(models.TimetableUser.id_timetable).filter(
        models.TimetableUser.id_user == user_id,
        models.TimetableUser.status == status).all()
    return [id[0] for id in timetables_id]


def get_amount_of_user_timetables(
        db: Session, user_id: int | Column[Integer]) -> int:
    """Отдаёт количество расписаний пользователя"""
    return db.query(func.count(models.TimetableUser.id_timetable)).filter(
        models.TimetableUser.id_user == user_id).scalar()


def get_timetable_users_id(
        db: Session, timetable_id: int | Column[Integer]) -> list[int]:
    """Отдаёт id всех пользователей, прикрепленных к данному расписанию"""
    users_id = db.query(models.TimetableUser.id_user).filter(
        models.TimetableUser.id_timetable == timetable_id).all()
    return [user_id[0] for user_id in users_id]


def get_public_information_about_users_in_timetable(
    db: Session,
    timetable_id: int | Column[Integer]
) -> list[models.User]:
    """Отдаёт почту, фамилию и имя пользователей в расписании из БД 
    по ID этого расписания"""
    users_public_info =  db.query(
        models.User.id, 
        models.User.email, 
        models.User.first_name, 
        models.User.last_name
    ).join(
        models.TimetableUser, 
        models.TimetableUser.id_timetable == timetable_id).all()

    return users_public_info


def exists_timetable_user_relation(
        db: Session, user_id: int | Column[Integer], 
        timetable_id: int | Column[Integer]) -> bool:
    """Проверяет, есть ли у данного пользователя данное расписание"""
    return db.query(exists().where(and_(
        models.TimetableUser.id_user == user_id,
        models.TimetableUser.id_timetable == timetable_id))).scalar()


def have_user_enough_rights_in_timetable(
        db: Session, user_id: int | Column[Integer], 
        timetable_id: int | Column[Integer],
        statuses: list[TimetableUserStatuses] = [TimetableUserStatuses.elder]
    ) -> bool:
    """Проверяет, есть ли у данного пользователя достаточно прав в данном
    расписании (т.е. проверяет статус пользователя в этом расписании). 
    Автоматически проверяется, является ли пользователь старостой
    в данном расписании. Можно изменить проверку статуса пользователя
    в расписании на другой или другие, если их несколько"""
    return db.query(exists().where(and_(
        models.TimetableUser.id_user == user_id,
        models.TimetableUser.id_timetable == timetable_id,
        models.TimetableUser.status.in_(statuses)))).scalar()


def delete_timetable_user_relation(
        db: Session, user_id: int | Column[Integer], 
        timetable_id: int | Column[Integer]):
    """Открепляет пользователя от расписания"""
    db.query(models.TimetableUser).filter(
        models.TimetableUser.id_user == user_id,
        models.TimetableUser.id_timetable == timetable_id).delete()
    db.commit()
