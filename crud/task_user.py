from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, and_, exists

from sql.models import TaskStatuses
from models.schemas import TaskStatusesEnum


def create_task_user_status(
        db: Session, 
        task_id: int | Column[Integer], 
        user_id: int | Column[Integer],
        status: TaskStatusesEnum = TaskStatusesEnum.in_progress
    ):
    """Создаёт статус пользователя в данной задаче в БД. 
    Автоматически стоит статус "в процессе", который можно поменять"""
    db_task_user_status = TaskStatuses(
        id_task = task_id,
        id_user = user_id,
        status = status
    )
    db.add(db_task_user_status)
    db.commit()


def update_task_user_status(
        db: Session,
        task_id: int | Column[Integer],
        user_id: int | Column[Integer],
        status: TaskStatusesEnum
    ):
    """Обновляет статус задачи для пользователя в БД"""
    db.query(TaskStatuses).filter(
        TaskStatuses.id_task == task_id, 
        TaskStatuses.id_user == user_id
    ).update(
        {
            TaskStatuses.status: status
        },
        synchronize_session=False
    )
    db.commit()


def get_task_user_status(
        db: Session,
        task_id: int | Column[Integer],
        user_id : int | Column[Integer]) -> TaskStatusesEnum | None:
    """Возвращает статус пользователя в данной задаче"""
    return db.query(TaskStatuses.status).filter(
        TaskStatuses.id_task == task_id,
        TaskStatuses.id_user == user_id).scalar()


def is_task_attached_to_user(
        db: Session, task_id: int | Column[Integer],
        user_id : int | Column[Integer]) -> bool:
    """Проверяет, есть ли у данного пользователя данная задача"""
    return db.query(exists().where(and_(
        TaskStatuses.id_task == task_id,
        TaskStatuses.id_user == user_id))).scalar()
