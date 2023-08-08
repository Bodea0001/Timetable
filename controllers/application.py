from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer

from models.schemas import (
    UserApplication,
    TimetableUserCreate,
    TimetableUserStatuses,
    ApplicationForConsideration,
)
from sql.models import Application
from crud.timetable_user import (
    create_timetable_user_relation,
    get_user_timetables_id_by_status
)
from crud.timetable import get_timetable_by_id
from crud.user import get_public_information_about_user
from crud.application import get_applications_by_list_with_timetables_id
from controllers.timetable import get_valid_timetable_lite


def accept_application(
        db: Session,
        application: Application,
        status: TimetableUserStatuses = TimetableUserStatuses.user):
    """Одобряет заявку пользователя на добавление к расписанию, т.е. добавляет
    пользователя в расписание со статусом "пользователь" (можно изменить 
    при помощи параметра "status")"""
    timetable_user_relation = TimetableUserCreate(
        id_user = application.id_user,  # type: ignore
        id_timetable = application.id_timetable,  # type: ignore
        status = status
    )
    create_timetable_user_relation(db, timetable_user_relation)


def _validate_user_application(
        db: Session, application: Application) -> UserApplication:
    "Отдает пользователю его заявку на добавление к расписанию в нормальном виде"
    db_timetable = get_timetable_by_id(db, application.id_timetable)  # type: ignore
    timetable = get_valid_timetable_lite(db, db_timetable)
    return UserApplication(
        id=application.id,  # type: ignore
        id_timetable=application.id_timetable,  # type: ignore
        creation_date=application.creation_date,  #type: ignore
        timetable=timetable
    )


def get_valid_user_applications(
        db: Session, applications: list[Application]) -> list[UserApplication]:
    """Отдаёт список из заявок пользователя в нормальном виде"""
    return [_validate_user_application(db, application) 
            for application in applications]


def get_valid_applications_for_consideration(
        db: Session, user_id: int | Column[Integer]
    ) -> list[ApplicationForConsideration]:
    """Отдаёт пользователю список из заявок на рассмотрение в нормальном виде"""
    applications = _get_applications_for_consideration(db, user_id)
    return [_validate_application_for_consideration(db, application)
            for application in applications]


def _validate_application_for_consideration(
        db: Session, application: Application) -> ApplicationForConsideration:
    """Отдает пользователю, владеющим расписанием, заявку 
    на добавление к расписанию в нормальном виде"""
    user_public_info = get_public_information_about_user(
        db, application.id_user)  # type: ignore
    return ApplicationForConsideration(
        id=application.id,  # type: ignore
        user_email=user_public_info.email,  # type: ignore
        user_first_name=user_public_info.first_name,  # type: ignore
        user_last_name=user_public_info.last_name,  # type: ignore
        id_timetable=application.id_timetable,  # type: ignore
        creation_date=application.creation_date  #type: ignore
    )


def _get_applications_for_consideration(
        db: Session, user_id: int | Column[Integer]) -> list[Application]:
    """Отдаёт пользователю список из заявок на рассмотрение"""
    timetables_id = get_user_timetables_id_by_status(
        db, user_id, TimetableUserStatuses.elder)
    return get_applications_by_list_with_timetables_id(db, timetables_id)
