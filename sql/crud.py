from sqlalchemy.orm import Session
from sqlalchemy import select

from sql import models
from models import schemas
from sql.database import SessionLocal, engine


def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.email == username).first()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        email=user.email,
        password=user.password,
        first_name=user.first_name,
        last_name=user.last_name,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_task(db: Session, task: schemas.TaskBase):
    db_task = models.Task(
        id_timetable=task.timetable_id,
        description=task.description,
        deadline=task.deadline,
        subject=task.subject
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def get_task_by_subject(db: Session, id_timetable: int, subject: str):
    result = db.execute(select(models.Task).where(models.Task.subject == subject).where(models.Task.id_timetable ==
                                                                                        id_timetable))
    return result.scalars().all()


def get_all_tasks_in_table(db: Session, id_timetable: int):
    result = db.execute(select(models.Task).where(models.Task.id_timetable == id_timetable))
    return result.scalars().all()


def delete_task_from_table(db: Session, id_timetable: int, id_task: int):
    db.query(models.Task).filter(models.Task.id == id_task).filter(models.Task.id_timetable == id_timetable).delete()
    db.commit()
    return 'Task deleted successfully'
