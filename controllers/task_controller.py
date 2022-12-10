from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from models import schemas
from sql.crud import create_task


def addTask(task: schemas.TaskBase, db: Session):
    create_task(db, task)
    return HTTPException(status_code=201, detail='Task created successfully')
