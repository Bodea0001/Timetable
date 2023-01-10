from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from models import schemas
from controllers.user import get_current_user
from controllers.db import get_db
from controllers.task_controller import addTask, addTaskForAll, getTaskBySubject, getAllTaskInTable,\
    deleteTaskFromTable, get_task_by_userid, deleteTaskFromUser, deleteReadyTaskFromUser, deleteReadyTaskFromTimeTable

router = APIRouter()


# Add new task for one user
@router.post("/task/user", tags=["task"], status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_current_user)])
async def create_task(task: schemas.TaskOut, db: Session = Depends(get_db),
                      user: schemas.User = Depends(get_current_user)):
    return addTask(task, db, user.id)


# Add new task for all users in timetable
@router.post("/task/all", tags=["task"], status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_current_user)])
async def create_task_for_all(task: schemas.TaskBase, db: Session = Depends(get_db)):
    return addTaskForAll(task, db)


# Get tasks by subject in timetable
@router.get('/task/subject', tags=['task'], status_code=status.HTTP_200_OK,
            dependencies=[Depends(get_current_user)])
async def get_task_by_subject(subject: str, id_timetable: int, db: Session = Depends(get_db)):
    return getTaskBySubject(subject, id_timetable, db)


# Get all users tasks in all timetables
@router.get('/task/user_id', tags=['task'], status_code=status.HTTP_200_OK,
            dependencies=[Depends(get_current_user)])
async def get_task_by_user_id(db: Session = Depends(get_db), user: schemas.User = Depends(get_current_user)):
    return get_task_by_userid(db, user.id)


# Get all users tasks in timetable
@router.get('/task', tags=['task'], status_code=status.HTTP_200_OK,
            dependencies=[Depends(get_current_user)])
async def get_task(id_timetable: int, db: Session = Depends(get_db), user: schemas.User = Depends(get_current_user)):
    return getAllTaskInTable(id_timetable, db, user.id)


# Delete task from all users in timetable
@router.delete('/task/all', tags=['task'], status_code=status.HTTP_200_OK, dependencies=[Depends(get_current_user)])
async def delete_task(id_timetable: int, id_task: int, db: Session = Depends(get_db)):
    return deleteTaskFromTable(id_timetable, id_task, db)


# Delete task from user in timetable
@router.delete('/task/single', tags=['task'], status_code=status.HTTP_200_OK, dependencies=[Depends(get_current_user)])
async def delete_task(id_timetable: int, id_task: int, db: Session = Depends(get_db),
                      user: schemas.User = Depends(get_current_user)):
    return deleteTaskFromUser(id_timetable, id_task, db, user.id)


# Delete ready task from user in timetable
@router.delete('/task/ready/single', tags=['task'], status_code=status.HTTP_200_OK,
               dependencies=[Depends(get_current_user)])
async def delete_task(id_timetable: int, db: Session = Depends(get_db),
                      user: schemas.User = Depends(get_current_user)):
    return deleteReadyTaskFromUser(id_timetable, db, user.id)


# Delete ready task from all users in timetable
@router.delete('/task/ready/all', tags=['task'], status_code=status.HTTP_200_OK,
               dependencies=[Depends(get_current_user)])
async def delete_task(id_timetable: int, db: Session = Depends(get_db)):
    return deleteReadyTaskFromTimeTable(id_timetable, db)
