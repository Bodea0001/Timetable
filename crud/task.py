from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy import Column, Date, Integer, String, and_, cast, exists

from sql import models
from models import schemas


def create_task(
    db: Session, 
    user_id: int | Column[Integer], 
    task: schemas.TaskBase,
    tag: schemas.TaskTags
):
    """Создаёт задачу в расписании в БД"""
    db_task = models.Task(
        id_timetable = task.id_timetable,
        description = task.description,
        subject = task.subject,
        deadline = task.deadline,
        tag = tag
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    _create_task_user_status(db, db_task.id, user_id)


def _create_task_user_status(
    db: Session, 
    task_id: int | Column[Integer], 
    user_id: int | Column[Integer],
    status: schemas.TaskStatusesEnum = schemas.TaskStatusesEnum.in_progress
):
    """Создаёт статус пользователя в данной задаче в БД. 
    Автоматически стоит статус "в процессе", который можно поменять"""
    db_task_user_status = models.TaskStatuses(
        id_task = task_id,
        id_user = user_id,
        status = status
    )
    db.add(db_task_user_status)
    db.commit()


def create_tasks_user_relation_in_timetable(
    db: Session, 
    timetable_id: int | Column[Integer], 
    user_id: int | Column[Integer]
):
    """Для данного пользователя добавляет все задачи 
    с тегом "все" из данного расписания в БД"""
    tasks_id_with_tag_all_in_timetable = db.query(models.Task.id).filter(
        models.Task.id_timetable == timetable_id,
        models.Task.tag == schemas.TaskTags.all).all()
    sorted_tasks_id = [task[0] for task in tasks_id_with_tag_all_in_timetable]
    for task_id in sorted_tasks_id:
        _create_task_user_status(db, task_id, user_id)


def update_task_user_status(
    db: Session,
    task_id: int | Column[Integer],
    user_id: int | Column[Integer],
    status: schemas.TaskStatusesEnum
):
    """Обновляет статус задачи для пользователя в БД"""
    db.query(models.TaskStatuses).filter(
        models.TaskStatuses.id_task == task_id, 
        models.TaskStatuses.id_user == user_id
    ).update(
        {
            models.TaskStatuses.status: status
        },
        synchronize_session=False
    )
    db.commit()


def update_task_info(
    db: Session,
    task_id: int | Column[Integer],
    description: str | Column[String],
    subject:  str | Column[String],
    deadline:  datetime,
):
    """Обновляет информацию о задачи в БД"""
    db.query(models.Task).filter(models.Task.id == task_id).update(
        {
            models.Task.description: description,
            models.Task.subject: subject,
            models.Task.deadline: deadline,
        },
        synchronize_session=False
    )
    db.commit()


def exists_user_task_relation(
    db: Session,
    task_id: int | Column[Integer],
    user_id : int | Column[Integer]
) -> bool:
    """Проверяет, есть ли у данного пользователя данная задача"""
    return db.query(exists().where(and_(
        models.TaskStatuses.id_task == task_id,
        models.TaskStatuses.id_user == user_id))).scalar()


def get_task_by_id(db: Session,
    task_id: int | Column[Integer]
) -> models.Task | None:
    """Ищет в БД задачу по ID и отдаёт"""
    return db.query(models.Task).filter(models.Task.id == task_id).first()


def get_complited_tasks_id_by_user_id_and_timetable_id(
    db: Session,
    user_id: int | Column[Integer],
    timetable_id: int | Column[Integer]
) -> list[int] | None:
    """Ищет у пользователя в расписании выполненые задачи и отдаёт"""
    user_tasks = db.query(models.TaskStatuses.id_task).filter(
        models.TaskStatuses.id_user == user_id,
        models.TaskStatuses.status == schemas.TaskStatusesEnum.complited
    ).all()
    user_tasks = [task[0] for task in user_tasks]
    user_timetable_tasks = db.query(models.Task.id).filter(
        models.Task.tag == schemas.TaskTags.one,
        models.Task.id_timetable == timetable_id,
        models.Task.id.in_(user_tasks)
    ).all()
    return [task[0] for task in user_timetable_tasks]


def get_tasks_by_date(
    db: Session,
    timetable_id: int | Column[Integer], 
    tasks_date: date,
    user_id: int | Column[Integer]
) -> list[models.Task] | None:
    """Ищет задачи пользователя в расписании на определенную дату"""
    return db.query(models.Task).join(
        models.TaskStatuses,
        models.TaskStatuses.id_user == user_id
    ).filter(
        models.Task.id_timetable == timetable_id,
        cast(models.Task.deadline, Date) == tasks_date,
    ).all()


def delete_task_by_id(db: Session, task_id: int | Column[Integer]):
    """Удаляет задачу в БД по ID"""
    db.query(models.Task).filter(models.Task.id == task_id).delete()
    db.commit()


def delete_tasks_by_list_with_id(db: Session, task_ids: list[int]):
    """Удаляет задачи по переданному списку с ID"""
    db.query(models.Task).filter(models.Task.id.in_(task_ids)).delete()
    db.commit()
