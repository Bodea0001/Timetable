from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer

from sql import models
from sql.crud import (
    create_task,
    get_user_lite_by_id,
    get_task_by_subject,
    get_timetable_by_id,
    create_task_for_all,
    get_tasks_by_user_id,
    delete_task_from_user,
    get_all_tasks_in_table,
    delete_task_from_table,
    delete_ready_task_from_user,
    delete_ready_task_from_timetable,
)
from models import schemas


def addTask(task: schemas.TaskBase, db: Session, user_id: int):
    check_task_status(task.statuses[0].status)  # type: ignore
    create_task(db, task, user_id)
    return HTTPException(status_code=201, detail='Task created successfully')


def addTaskForAll(task: schemas.TaskBase, db: Session):
    create_task_for_all(db, task)
    return HTTPException(status_code=201, detail='Task created successfully')


def check_task_status(task_status: schemas.TaskStatusesEnum) -> None:
    statuses = schemas.TaskStatusesEnum._value2member_map_.keys()
    if task_status not in statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid task status"
        )


def getTaskBySubject(subject: str, id_timetable: int, db: Session):
    return get_task_by_subject(db, id_timetable, subject)


def get_task_by_userid(db: Session, user_id: int):
    return get_tasks_by_user_id(db, user_id)


def getAllTaskInTable(id_timetable: int, db: Session, user_id: int):
    return get_all_tasks_in_table(db, id_timetable, user_id)


def deleteTaskFromTable(id_timetable: int, id_task: int, db: Session):
    delete_task_from_table(db, id_timetable, id_task)
    return HTTPException(status_code=200, detail='Task deleted successfully')


def deleteTaskFromUser(id_timetable: int, id_task: int, db: Session, user_id: int):
    delete_task_from_user(db, id_timetable, id_task, user_id)
    return HTTPException(status_code=200, detail='Task deleted successfully')


def deleteReadyTaskFromUser(id_timetable: int, db: Session, user_id: int):
    delete_ready_task_from_user(db, id_timetable, user_id)
    return HTTPException(status_code=200, detail='Task deleted successfully')


def deleteReadyTaskFromTimeTable(id_timetable: int, db: Session):
    delete_ready_task_from_timetable(db, id_timetable)
    return HTTPException(status_code=200, detail='Task deleted successfully')


def get_valid_task(db: Session, task: schemas.TaskBase):
    timetable = get_timetable_by_id(db, task.id_timetable)
    if not timetable:
        raise HTTPException(
            status_code=404,
            detail=f'Timetable with id = {task.id_timetable} was not found'
        )
    return HTTPException(
        status_code=200,
        detail='Timetable was found'
    )

def validate_task_for_user(task: models.Task, user_id: int | Column[Integer]) -> schemas.TaskOutForUser | None:
    for task_status in task.statuses:  # type: ignore
        if task_status.id_task == task.id and task_status.id_user == user_id:
            user_task_status = task_status.status
            return schemas.TaskOutForUser(
                id=task.id,  # type: ignore
                id_timetable= task.id_timetable,  # type: ignore
                subject=task.subject,  # type: ignore
                description=task.description,  # type: ignore
                deadline=task.deadline,  # type: ignore
                tag=task.tag,  # type: ignore
                status=user_task_status,  # type: ignore
                creation_date=task.creation_date,  # type: ignore
            )


def validate_task_for_elder(db: Session, task: models.Task) -> schemas.TaskOutForElder:
    valid_task_statuses = validate_task_statuses(db, task.statuses)  # type: ignore
    return schemas.TaskOutForElder(
        id=task.id,  # type: ignore
        id_timetable= task.id_timetable,  # type: ignore
        subject=task.subject,  # type: ignore
        description=task.description,  # type: ignore
        deadline=task.deadline,  # type: ignore
        tag=task.tag,  # type: ignore
        statuses=valid_task_statuses,
        creation_date=task.creation_date,  # type: ignore
    )


def validate_task_statuses(db: Session, task_statuses: list[models.TaskStatuses]) -> list[schemas.TaskStatusesOut]:
    valid_task_statuses = []
    for task_status in task_statuses:
        user_info = get_user_lite_by_id(db, task_status.id_user)  # type: ignore
        if user_info:
            email, first_name, last_name = user_info
        else:
            email, first_name, last_name = (None, None, None)
        valid_task_status = schemas.TaskStatusesOut(
            id=task_status.id,  # type: ignore
            id_user=task_status.id_user,  # type: ignore
            status=task_status.status,  # type: ignore
            user_email=email,  # type: ignore
            user_first_name=first_name,  # type: ignore
            user_last_name=last_name,  # type: ignore
        )
        valid_task_statuses.append(valid_task_status)
    return valid_task_statuses
