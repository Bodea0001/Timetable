from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer

from sql import models
from models.schemas import (
    TaskOutForUser,
    TaskOutForElder,
    TaskStatusesOut,
    TimetableUserStatuses
)
from crud.task import (
    get_task_by_id,
    get_tasks_by_date,
    get_tasks_in_timetable,
    get_user_tasks_in_timetable
)
from crud.timetable_user import (
    get_timetable_user_status,
    exists_timetable_user_relation
)
from crud.task_user import get_task_user_status
from crud.user import get_public_information_about_user


def is_all_users_attached_to_timetable(
        db: Session, user_ids: list[int], timetable_id: int) -> bool:
    """Проверяет, все ли пользователи прикреплены к расписанию"""
    timetable_users_relation = []
    
    for user_id in user_ids:
        timetable_user_relation = exists_timetable_user_relation(
            db, user_id, timetable_id)
        timetable_users_relation.append(timetable_user_relation)
    
    return all(timetable_users_relation)

def get_valid_task(
        db: Session, task: models.Task, user_id: int | Column[Integer], 
        timetable_user_status: TimetableUserStatuses
    ) -> TaskOutForUser | TaskOutForElder:
    """Валидирует и отдаёт задачу (валидирует задачу по статусу пользователя 
    в расписании, т.е. для обычных пользователей и старост)"""
    match timetable_user_status:
        case TimetableUserStatuses.user:
            return _validate_task_for_user(db, task, user_id)
        case TimetableUserStatuses.elder:
            return _validate_task_for_elder(db, task)


def get_valid_task_by_id(
        db: Session, task_id: int | Column[Integer],
        user_id: int | Column[Integer], timetable_id: int | Column[Integer]
    ) -> TaskOutForUser | TaskOutForElder:
    """Находит задачу по ее ID и валидирует эту задачу по статусу пользователя 
    в расписании, т.е. для обычных пользователей и старост)"""
    task = get_task_by_id(db, task_id)
    timetable_user_status = get_timetable_user_status(db, user_id, timetable_id)

    return get_valid_task(db, task, user_id, timetable_user_status)  # type: ignore


def get_valid_tasks_in_timetable(
        db: Session, timetable_id: int | Column[Integer],
        user_id: int | Column[Integer], 
    ) -> list[TaskOutForUser] | list[TaskOutForElder]:
    """Валидирует и отдаёт задачи в расписании (валидирует задачи по статусу 
    пользователя в расписании, т.е. для обычных пользователей и старост)"""
    timetable_user_status = get_timetable_user_status(db, user_id, timetable_id)
    
    match timetable_user_status:
        case TimetableUserStatuses.user:
            tasks = get_user_tasks_in_timetable(db, timetable_id, user_id)
            print([task.id for task in tasks])
            return [_validate_task_for_user(db, task, user_id) for task in tasks]
        case TimetableUserStatuses.elder:
            tasks = get_tasks_in_timetable(db, timetable_id)
            return [_validate_task_for_elder(db, task) for task in tasks]


def get_valid_tasks_in_timetable_by_date(
        db: Session, timetable_id: int | Column[Integer],
        date: date, user_id: int | Column[Integer]
    ) -> list[TaskOutForUser] | list[TaskOutForElder] | None:
    """Валидирует и отдаёт задачи по дате в расписании (валидирует задачи по 
    статусу пользователя в расписании, т.е. для обычных пользователей и старост)"""
    tasks = get_tasks_by_date(db, timetable_id, date, user_id)
    timetable_user_status = get_timetable_user_status(db, user_id, timetable_id)

    match timetable_user_status:
        case TimetableUserStatuses.user:
            return [_validate_task_for_user(db, task, user_id) for task in tasks]
        case TimetableUserStatuses.elder:
            return [_validate_task_for_elder(db, task) for task in tasks]


def _validate_task_for_user(
        db: Session, task: models.Task, 
        user_id: int | Column[Integer]) -> TaskOutForUser:
    """Валидирует задачу для пользователя расписания"""
    task_user_status = get_task_user_status(db, task.id, user_id)
    return TaskOutForUser(
        id=task.id,  # type: ignore
        id_timetable= task.id_timetable,  # type: ignore
        subject=task.subject,  # type: ignore
        description=task.description,  # type: ignore
        deadline=task.deadline,  # type: ignore
        status=task_user_status,  # type: ignore
        creation_date=task.creation_date,  # type: ignore
    )


def _validate_task_for_elder(db: Session, task: models.Task) -> TaskOutForElder:
    """Валидирует задачу для старосты расписания"""
    valid_task_statuses = _validate_task_statuses(db, task.statuses)  # type: ignore
    return TaskOutForElder(
        id=task.id,  # type: ignore
        id_timetable= task.id_timetable,  # type: ignore
        subject=task.subject,  # type: ignore
        description=task.description,  # type: ignore
        deadline=task.deadline,  # type: ignore
        statuses=valid_task_statuses,
        creation_date=task.creation_date,  # type: ignore
    )


def _validate_task_statuses(
        db: Session, task_statuses: list[models.TaskStatuses]
    ) -> list[TaskStatusesOut]:
    """Валидирует статусы всех пользователей, прикрепленных к задаче"""
    valid_task_users_statuses = []

    for task_status in task_statuses:
        valid_task_user_status = _validate_task_status(db, task_status)
        valid_task_users_statuses.append(valid_task_user_status)

    return valid_task_users_statuses


def _validate_task_status(
        db: Session, task_status: models.TaskStatuses) -> TaskStatusesOut:
    """Валидирует стутус одного пользователя, прикрепленного к задаче"""
    user_public_info = get_public_information_about_user(
        db, task_status.id_user)  # type: ignore        
    return TaskStatusesOut(
        id=task_status.id,  # type: ignore
        id_user=task_status.id_user,  # type: ignore
        status=task_status.status,  # type: ignore
        user_email=user_public_info.email,  # type: ignore
        user_first_name=user_public_info.first_name,  # type: ignore
        user_last_name=user_public_info.last_name,  # type: ignore
    )
