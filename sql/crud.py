from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session
from sqlalchemy import select

from sql import models
from models import schemas


def get_user(db: Session, username: str | Column[String]) -> models.User | None:
    return db.query(models.User).filter(models.User.email == username).first()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
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


def get_timetable_by_name_and_user_id(
    db: Session,
    timetable_name: str | Column[String],
    user_id: int | Column[Integer],
    ) -> models.Timetable | None:
    return db.query(models.Timetable).join(
        models.TimetableUser,
        models.TimetableUser.id_user == user_id
        ).filter(models.Timetable.name == timetable_name).first()

def get_timetable_by_name_university_id_specialization_id_course(
    db: Session,
    name: str | Column[String],
    university_id: int | Column[Integer],
    specialization_id: int | Column[Integer],
    course: int | Column[Integer],
    ) -> models.Timetable | None:
    return db.query(models.Timetable).filter(
        models.Timetable.name == name,
        models.Timetable.id_university == university_id,
        models.Timetable.id_specialization == specialization_id,
        models.Timetable.course == course
    ).first()


def create_timetable(db: Session, timetable: schemas.TimetableCreate) -> models.Timetable:
    db_timetable = models.Timetable(
        name = timetable.name,
        id_university = timetable.id_university,
        id_specialization = timetable.id_specialization,
        course = timetable.course,
    )
    db.add(db_timetable)
    db.commit()
    db.refresh(db_timetable)
    return db_timetable


def create_timetable_user(db: Session, timetable_user_relation: schemas.TimetableUser):
    db_timetable_user_relation = models.TimetableUser(
        id_user = timetable_user_relation.id_user,
        id_timetable = timetable_user_relation.id_timetable,
        status = timetable_user_relation.status
    )
    db.add(db_timetable_user_relation)
    db.commit()


def get_university(db: Session, university_name: str | Column[String]) -> models.University | None:
    return db.query(models.University).filter(models.University.name == university_name).first()


def get_university_by_id(db: Session, university_id: int | Column[Integer]) -> models.University | None:
    return db.query(models.University).filter(models.University.id == university_id).first()


def get_specialization_by_name(
    db: Session,
    specialization_name: str | Column[String],
    education_level: schemas.Education_level
    ) -> models.Specialization | None:
    return db.query(models.Specialization).filter(
        models.Specialization.name == specialization_name,
        models.Specialization.education_level == education_level,
        ).first()


def get_specialization_by_code(
    db: Session,
    specialization_code: str | Column[String],
    education_level: schemas.Education_level) -> models.Specialization | None:
    return db.query(models.Specialization).filter(
        models.Specialization.code == specialization_code,
        models.Specialization.education_level == education_level
        ).first()


def get_specialization_by_id(db: Session, specialization_id: int | Column[Integer]) -> models.Specialization | None:
    return db.query(models.Specialization).filter(models.Specialization.id == specialization_id).first()
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
