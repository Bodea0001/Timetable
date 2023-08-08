from datetime import date
from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, status, Depends, Path, Query

from sql import models
from models import schemas
from models.schemas import (
    TaskCreate,
    TaskOutForUser,
    TaskOutForElder,
    TimetableUserStatuses,
)
from crud.task_user import (
    update_task_user_status,
    is_task_attached_to_user
)
from crud.task import (
    create_task,
    update_task_info,
    delete_task_by_id,
    exists_task_with_id,
    is_user_task_creator,
    is_task_attached_to_timetable
)
from crud.timetable_user import (
    get_timetable_user_status,
    exists_timetable_user_relation
)
from controllers.db import get_db
from controllers.user import get_current_user
from controllers.task_controller import (
    get_valid_task,
    get_valid_task_by_id,
    get_valid_tasks_in_timetable,
    is_all_users_attached_to_timetable,
    get_valid_tasks_in_timetable_by_date,
)
from message import (
    TASK_DELETED,
    TASK_NOT_FOUND,
    TASKS_NOT_FOUND,
    USER_IS_NOT_TASK_CREATOR,
    USER_DOESNT_HAVE_TIMETABLE,
    TASK_IS_NOT_ATTACHED_TO_USER,
    TASK_IS_NOT_ATTACHED_TO_TIMETABLE,
    USERS_CANT_CREATE_TASKS_FOR_OTHER,
    NOT_ALL_USERS_ARE_ATTACHED_TO_TIMETALBE
)


router = APIRouter(prefix="/timetable/{timetable_id}/task", tags=["task"])


@router.post(
    path="/create",
    summary="Создаёт задачу в расписании",
    status_code=status.HTTP_201_CREATED,
    response_model=TaskOutForUser | TaskOutForElder)
async def create_task_in_timetable(
    task: TaskCreate,
    timetable_id: int = Path(gt=0),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    if not exists_timetable_user_relation(db, user.id, timetable_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=USER_DOESNT_HAVE_TIMETABLE)

    timetable_user_status = get_timetable_user_status(db, user.id, timetable_id)
    if (timetable_user_status == TimetableUserStatuses.user and 
        [user.id] != task.id_users):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=USERS_CANT_CREATE_TASKS_FOR_OTHER)
    
    if (timetable_user_status == TimetableUserStatuses.elder and
        not is_all_users_attached_to_timetable(db, task.id_users, timetable_id)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=NOT_ALL_USERS_ARE_ATTACHED_TO_TIMETALBE)

    task = create_task(db, timetable_id, task, user.id)

    return get_valid_task(db, task, user.id, timetable_user_status)  # type: ignore


@router.get(
    path="",
    summary="Отдаёт все задачи пользователю или старосте расписания",
    status_code=status.HTTP_200_OK,
    response_model=list[TaskOutForUser] | list[TaskOutForElder])
async def get_timetable_tasks_for_elder(
    timetable_id: int = Path(gt=0),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    if not exists_timetable_user_relation(db, user.id, timetable_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=USER_DOESNT_HAVE_TIMETABLE)
    
    tasks = get_valid_tasks_in_timetable(db, timetable_id, user.id)
    if not tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=TASKS_NOT_FOUND)

    return tasks


@router.get(
    path="/filter",
    summary="Фильтрует задачи расписания по дате",
    status_code=status.HTTP_200_OK,
    response_model=list[TaskOutForUser])
async def filter_user_tasks_by_date(
    timetable_id: int = Path(gt=0),
    date: date = Query(),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    if not exists_timetable_user_relation(db, user.id, timetable_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=USER_DOESNT_HAVE_TIMETABLE)

    tasks = get_valid_tasks_in_timetable_by_date(db, timetable_id, date, user.id)
    if not tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=TASKS_NOT_FOUND)

    return tasks


@router.patch(
    path="/{task_id}/update/status",
    summary="Обновляет статус задачи у пользователя",
    status_code=status.HTTP_200_OK,
    response_model=TaskOutForUser | TaskOutForElder)
async def update_user_status_in_task(
    task_status: schemas.TaskStatusesEnum,
    timetable_id: int = Path(gt=0),
    task_id: int = Path(gt=0),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    if not is_task_attached_to_timetable(db, timetable_id, task_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=TASK_IS_NOT_ATTACHED_TO_TIMETABLE)

    if not is_task_attached_to_user(db, task_id, user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=TASK_IS_NOT_ATTACHED_TO_USER)
    
    update_task_user_status(db, task_id, user.id, task_status)

    return get_valid_task_by_id(db, task_id, user.id, timetable_id)


@router.patch(
    path="{task_id}/update/info",
    summary="Update task's information",
    status_code=status.HTTP_200_OK,
    response_model=TaskOutForUser | TaskOutForElder)
async def update_task_information(
    task_data: schemas.TaskUpdate,
    task_id: int = Path(gt=0),
    timetable_id: int = Path(gt=0),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    if not exists_task_with_id(db, task_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=TASK_NOT_FOUND)

    if not is_task_attached_to_timetable(db, timetable_id, task_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=TASK_IS_NOT_ATTACHED_TO_TIMETABLE)

    if not is_user_task_creator(db, user.id, task_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=USER_IS_NOT_TASK_CREATOR)
    
    update_task_info(db, task_id, task_data)

    return get_valid_task_by_id(db, task_id, user.id, timetable_id)  


@router.delete(
    path="{task_id}/delete", 
    summary="Удаляет задачу из расписания",
    status_code=status.HTTP_200_OK,
    response_description=TASK_DELETED)
async def delete_task(
    task_id: int = Path(gt=0),
    timetable_id: int = Path(gt=0),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    if not exists_task_with_id(db, task_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=TASK_NOT_FOUND)

    if not is_task_attached_to_timetable(db, timetable_id, task_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=TASK_IS_NOT_ATTACHED_TO_TIMETABLE)

    if not is_user_task_creator(db, user.id, task_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=USER_IS_NOT_TASK_CREATOR)

    delete_task_by_id(db, task_id)
