from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

import models.schemas
from models import schemas
from sql.crud import create_task, get_task_by_subject, get_all_tasks_in_table, delete_task_from_table, \
    get_timetable_byid, get_tasks_by_user_id


def addTask(task: schemas.TaskBase, db: Session):
    create_task(db, task)
    return HTTPException(status_code=201, detail='Task created successfully')


def getTaskBySubject(subject: str, id_timetable: int, db: Session):
    return get_task_by_subject(db, id_timetable, subject)


def get_task_by_userid(db: Session, user_id: int):
    return get_tasks_by_user_id(db, user_id)


def getAllTaskInTable(id_timetable: int, db: Session):
    return get_all_tasks_in_table(db, id_timetable)


def deleteTaskFromTable(id_timetable: int, id_task: int, db: Session):
    delete_task_from_table(db, id_timetable, id_task)
    return HTTPException(status_code=200, detail='Task deleted successfully')


def get_valid_task(db: Session, task: models.schemas.TaskBase):
    timetable = get_timetable_byid(db, task.timetable_id)
    if not timetable:
        raise HTTPException(
            status_code=404,
            detail=f'Timetable with id = {task.timetable_id} was not found'
        )
    return HTTPException(
        status_code=200,
        detail='Timetable was found'
    )
