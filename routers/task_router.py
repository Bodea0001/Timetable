from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import date

from sql import models
from sql.crud import (
    get_task_by_id,
    update_task_info,
    get_tasks_by_date,
    delete_task_by_id,
    get_timetable_users_id,
    update_task_user_status,
    create_task_for_one_user,
    get_timetable_user_status,
    create_task_for_all_users,
    delete_tasks_by_list_with_id,
    get_user_task_relation_by_task_id,
    get_complited_task_ids_by_user_id_timetable_id,
)
from models import schemas
from controllers.user import get_current_user
from controllers.db import get_db
from controllers.task_controller import (
    validate_task_for_user,
    validate_task_for_elder,
)
from controllers.timetable import check_timetable

router = APIRouter(
    prefix="/task",
    tags=["task"]
)


@router.post(
    path="/create_for_user",
    status_code=status.HTTP_201_CREATED,
    summary="Create a task for one user in the timetable"
)
async def create_task_for_user(
    user_id: int,
    task: schemas.TaskBase,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    check_timetable(user, task.id_timetable)

    timetable_current_user_status = get_timetable_user_status(db, user.id, task.id_timetable)
    if (timetable_current_user_status != schemas.TimetableUserStatuses.elder or user_id != user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"The current user doesn't have access rights to create the task to transmitted user in this timetable"
        )

    create_task_for_one_user(db, user_id, task)


@router.post(
    path="/create_for_all",
    status_code=status.HTTP_201_CREATED,
    summary="Create a task for all users in the timetable"
)
async def create_task_for_all(
    task: schemas.TaskBase,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    check_timetable(user, task.id_timetable)

    timetable_user_status = get_timetable_user_status(db, user.id, task.id_timetable)
    if (timetable_user_status != schemas.TimetableUserStatuses.elder):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"The current user doesn't have access rights to create the task in this timetable"
        )
    
    users_id = get_timetable_users_id(db, task.id_timetable)   
    create_task_for_all_users(db, users_id, task)


@router.get(
    path="/get_in_timetable/for_user",
    response_model=list[schemas.TaskOutForUser],
    status_code=status.HTTP_200_OK,
    summary="Get user's tasks fin the timetable"
)
async def get_timetable_tasks_for_elder(
    timetable_id: int,
    user: models.User = Depends(get_current_user)
):
    timetable = check_timetable(user, timetable_id)
    
    user_timetable_tasks = [validate_task_for_user(task, user.id) for task in timetable.tasks]  # type: ignore
    user_timetable_sorted_tasks = [task for task in user_timetable_tasks if task]
    if user_timetable_sorted_tasks:
        return user_timetable_sorted_tasks
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No tasks for the user in this timetable"
        )


@router.get(
    path="/get_in_timetable/for_elder",
    response_model=list[schemas.TaskOutForElder],
    status_code=status.HTTP_200_OK,
    summary="Get timetable's tasks for elder"
)
async def get_user_tasks_in_timetable(
    timetable_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    timetable = check_timetable(user, timetable_id)

    timetable_user_status = get_timetable_user_status(db, user.id, timetable_id)
    if timetable_user_status != schemas.TimetableUserStatuses.elder:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"The current user doesn't have access rights to get all tasks in this timetable"
        )

    elder_timetable_tasks = [validate_task_for_elder(db, task) for task in timetable.tasks]  # type: ignore 
    elder_timetable_sorted_tasks = [task for task in elder_timetable_tasks if task]
    if elder_timetable_sorted_tasks:
        return elder_timetable_sorted_tasks
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No tasks for the elder in this timetable"
        )


@router.get(
    path="/get_all",
    response_model=list[schemas.TaskOutForUser],
    status_code=status.HTTP_200_OK,
    summary="Get all user's tasks"
)
async def get_all_user_tasks(user: models.User = Depends(get_current_user)):
    user_tasks = [validate_task_for_user(task, user.id) for timetable in user.timetables_info for task in timetable.tasks]  # type: ignore
    user_sorted_tasks = [task for task in user_tasks if task]
    if user_sorted_tasks:
        return user_sorted_tasks
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No tasks for the user"
        )


@router.get(
    path="/filter",
    response_model=list[schemas.TaskOutForUser],
    status_code=status.HTTP_200_OK,
    summary="Filter tasks in the timetable by date"
)
async def filter_user_tasks_by_date(
    timetable_id: int,
    tasks_date: date,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    check_timetable(user, timetable_id)

    tasks = get_tasks_by_date(db, timetable_id, tasks_date, user.id)
    if tasks:
        return [validate_task_for_user(task, user.id) for task in tasks]
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No tasks for the user in this timetable on the transmitted date"
        )


@router.patch(
    path="/update/status",
    status_code=status.HTTP_200_OK,
    summary="Update user's status in the task"
)
async def update_user_status_in_task(
    task_id: int,
    task_status: schemas.TaskStatusesEnum,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    user_task_relation = get_user_task_relation_by_task_id(db, task_id, user.id)
    if not user_task_relation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user doesn't have this task"
        )
    
    update_task_user_status(db, task_id, user.id, task_status)


@router.patch(
    path="/update/info",
    status_code=status.HTTP_200_OK,
    summary="Update task's information"
)
async def update_task_information(
    task_data: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    task = get_task_by_id(db, task_data.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unknown task"
        )
    elif task.id_timetable != task_data.id_timetable:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The transmitted timetable doesn't have this task"
        )

    user_task_relation = get_user_task_relation_by_task_id(db, task.id, user.id)
    if not user_task_relation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user doesn't have this task"
        )
    
    if task.tag == schemas.TaskTags.all:
        check_timetable(user, task.id_timetable)  # type: ignore

        timetable_user_status = get_timetable_user_status(db, user.id, task.id_timetable)  # type: ignore
        if timetable_user_status != schemas.TimetableUserStatuses.elder:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"The current user doesn't have access rights to update this task"
            )
    
    update_task_info(db, task_data.id, task_data.description, task_data.subject, task_data.deadline)


@router.delete("/delete", summary="Delete the task in the timetable")
async def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    task = get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unknown task"
        )
    
    check_timetable(user, task.id_timetable)  # type: ignore

    timetable_user_status = get_timetable_user_status(db, user.id, task.id_timetable)  # type: ignore
    user_task_relation = get_user_task_relation_by_task_id(db, task_id, user.id)
    if task.tag == schemas.TaskTags.one and not user_task_relation or timetable_user_status != schemas.TimetableUserStatuses.elder:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"The current user doesn't have access rights to delete this task in the timetable"
        )

    delete_task_by_id(db, task_id)


@router.delete("/delete/complited", summary="Delete complited tasks in the timetable")
async def delete_expired_user_tasks(
    timetable_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    check_timetable(user, timetable_id)  # type: ignore

    user_timetable_task_ids = get_complited_task_ids_by_user_id_timetable_id(db, user.id, timetable_id)
    if not user_timetable_task_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user has no complited tasks"
        )
    delete_tasks_by_list_with_id(db, user_timetable_task_ids)