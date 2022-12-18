from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from models import schemas
from controllers.user import get_current_user
from controllers.db import get_db
from controllers.task_controller import addTask, getTaskBySubject, getAllTaskInTable, deleteTaskFromTable, \
    get_task_by_userid

router = APIRouter()


# Add new  task
@router.post("/task", tags=["task"], response_model=schemas.TaskBase, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(get_current_user)])
async def create_task(task: schemas.TaskBase, db: Session = Depends(get_db)):
    return addTask(task, db)


# Get tasks by subject in timetable
@router.get('/task/subject', tags=['task'], response_model=schemas.TaskBase, status_code=status.HTTP_200_OK,
            dependencies=[Depends(get_current_user)])
async def get_task_by_subject(subject: str, id_timetable: int, db: Session = Depends(get_db)):
    return getTaskBySubject(subject, id_timetable, db)


# Get all users tasks
@router.get('/task/user_id', tags=['task'], status_code=status.HTTP_200_OK, dependencies=[Depends(get_current_user)])
async def get_task_by_user_id(db: Session = Depends(get_db), user: schemas.User = Depends(get_current_user)):
    return get_task_by_userid(db, user.id)


# Get tasks in timetable by timetable id
@router.get('/task', tags=['task'], response_model=schemas.TaskBase, status_code=status.HTTP_200_OK,
            dependencies=[Depends(get_current_user)])
async def get_task(id_timetable: int, db: Session = Depends(get_db)):
    return getAllTaskInTable(id_timetable, db)


# Delete task by id
@router.delete('/task', tags=['task'], status_code=status.HTTP_200_OK, dependencies=[Depends(get_current_user)])
async def delete_task(id_timetable: int, id_task: int, db: Session = Depends(get_db)):
    return deleteTaskFromTable(id_timetable, id_task, db)
