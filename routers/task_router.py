from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from models import schemas
from controllers.user import get_current_user
from controllers.db import get_db
from controllers.task_controller import addTask, getTaskBySubject

router = APIRouter()


# Add new  task
@router.post("/task", tags=["task"], status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_current_user)])
async def create_task(task: schemas.TaskBase, db: Session = Depends(get_db)):
    return addTask(task, db)


@router.get('/task/subject', tags=['task'], status_code=status.HTTP_200_OK, dependencies=[Depends(get_current_user)])
async def get_task_by_subject(subject: str, id_timetable: int, db: Session = Depends(get_db)):
    return getTaskBySubject(subject, id_timetable, db)
