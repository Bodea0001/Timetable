from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from models import schemas
from sql.crud import create_task, get_task_by_subject, get_all_tasks_in_table, delete_task_from_table


def addTask(task: schemas.TaskBase, db: Session):
    create_task(db, task)
    return HTTPException(status_code=201, detail='Task created successfully')


def getTaskBySubject(subject: str, id_timetable: int, db: Session):
    return get_task_by_subject(db, id_timetable, subject)


def getAllTaskInTable(id_timetable: int, db: Session):
    return get_all_tasks_in_table(db, id_timetable)


def deleteTaskFromTable(id_timetable: int, id_task: int, db: Session):
    delete_task_from_table(db, id_timetable, id_task)
    return HTTPException(status_code=200, detail='Task deleted successfully')
