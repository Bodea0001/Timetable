from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from models import schemas
from sql.crud import create_task, get_task_by_subject


def addTask(task: schemas.TaskBase, db: Session):
    create_task(db, task)
    return HTTPException(status_code=201, detail='Task created successfully')


def getTaskBySubject(subject: str, id_timetable: int, db: Session):
    return get_task_by_subject(db, id_timetable, subject)
