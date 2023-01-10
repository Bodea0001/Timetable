from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

import models.schemas
from models import schemas
from sql.crud import create_task, get_task_by_subject, get_all_tasks_in_table, delete_task_from_table, \
    get_timetable_by_id, get_tasks_by_user_id, create_task_for_all, delete_task_from_user, delete_ready_task_from_user,\
    delete_ready_task_from_timetable


def addTask(task: schemas.TaskOut, db: Session, user_id: int):
    check_task_status(task.statuses[0].status)
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


def get_valid_task(db: Session, task: models.schemas.TaskBase):
    timetable = get_timetable_by_id(db, task.timetable_id)
    if not timetable:
        raise HTTPException(
            status_code=404,
            detail=f'Timetable with id = {task.timetable_id} was not found'
        )
    return HTTPException(
        status_code=200,
        detail='Timetable was found'
    )
