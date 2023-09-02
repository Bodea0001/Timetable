from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import Column, Date, Integer, cast, exists, and_

from sql.models import Task, TaskStatuses
from models.schemas import TaskCreate, TaskUpdate
from crud.task_user import create_task_user_status


def create_task(
        db: Session, timetable_id: int, task: TaskCreate, 
        user_id: int | Column[Integer]) -> Task:
    """Создаёт задачу в расписании в БД"""
    db_task = Task(
        id_timetable = timetable_id,
        id_creator = user_id,
        description = task.description,
        subject = task.subject,
        deadline = task.deadline,
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    for user_id in task.id_users:
        create_task_user_status(db, db_task.id, user_id)

    return db_task


def update_task_info(
        db: Session, task_id: int | Column[Integer], task: TaskUpdate):
    """Обновляет информацию о задачи в БД"""
    db.query(Task).filter(Task.id == task_id).update(
        {
            Task.description: task.description,
            Task.subject: task.subject,
            Task.deadline: task.deadline,
        },
        synchronize_session=False
    )
    db.commit()


def get_task_by_id(db: Session,
    task_id: int | Column[Integer]
) -> Task | None:
    """Ищет в БД задачу по ID и отдаёт"""
    return db.query(Task).filter(Task.id == task_id).first()


def get_tasks_by_date(
        db: Session,
        timetable_id: int | Column[Integer], 
        tasks_date: date,
        user_id: int | Column[Integer]
    ) -> list[Task]:
    """Ищет задачи пользователя в расписании на определенную дату"""
    return db.query(Task).join(
        TaskStatuses,
        TaskStatuses.id_user == user_id
    ).filter(
        Task.id_timetable == timetable_id,
        cast(Task.deadline, Date) == tasks_date).all()


def get_tasks_in_timetable(
        db: Session, timetable_id: int | Column[Integer]) -> list[Task]:
    """Ищет и отдаёт все задачи из расписания"""
    return db.query(Task).filter(
        Task.id_timetable == timetable_id).all()


def get_user_tasks_in_timetable(
        db: Session, timetable_id: int | Column[Integer], 
        user_id: int | Column[Integer]) -> list[Task]:
    """Ищет и отдаёт задачи пользователя в расписании"""
    subquery = db.query(TaskStatuses.id_task).filter(
        TaskStatuses.id_user == user_id).all()
    
    task_ids = [task_id[0] for task_id in subquery]

    return db.query(Task).filter(
        Task.id.in_(task_ids), Task.id_timetable == timetable_id).all()


def is_task_attached_to_timetable(
        db: Session, timetable_id: int | Column[Integer], 
        task_id: int | Column[Integer]) -> bool:
    """Проверяет, прикреплена ли задача к расписанию"""
    return db.query(exists().where(and_(
        Task.id == task_id, 
        Task.id_timetable == timetable_id))).scalar()


def is_user_task_creator(
        db: Session, user_id: int | Column[Integer],
        task_id: int | Column[Integer]) -> bool:
    """Проверяет, является ли данный пользователь создателем данной задачи"""
    return db.query(exists().where(and_(
        Task.id == task_id,
        Task.id_creator == user_id))).scalar()


def exists_task_with_id(db: Session, task_id: int | Column[Integer]) -> bool:
    """Проверяет, существует ли задача с данным ID"""
    return db.query(exists().where(Task.id == task_id)).scalar()



def delete_task_by_id(db: Session, task_id: int | Column[Integer]):
    """Удаляет задачу в БД по ID"""
    db.query(Task).filter(Task.id == task_id).delete()
    db.commit()


def delete_tasks_by_list_with_id(db: Session, task_ids: list[int]):
    """Удаляет задачи по переданному списку с ID"""
    db.query(Task).filter(Task.id.in_(task_ids)).delete()
    db.commit()
