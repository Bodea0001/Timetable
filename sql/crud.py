from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session
from sqlalchemy import select

from sql import models
from models import schemas


def get_user(db: Session, username: str | Column[String]) -> models.User | None:
    return db.query(models.User).filter(models.User.email == username).first()


def update_user(db: Session, user_id: int | Column[Integer], user_data: schemas.UserUpdate):
    db.query(models.User).filter(models.User.id == user_id).update(
        {
            models.User.first_name: user_data.first_name,
            models.User.last_name: user_data.last_name,
        },
        synchronize_session=False
        )
    db.commit()  


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


def create_user_refresh_token(db: Session, user_id: int | Column[Integer], refresh_token: str | Column[String]) -> models.UserRefreshToken:
    db_user_refresh_token = models.UserRefreshToken(
        id_user = user_id,
        refresh_token = refresh_token
    )
    db.add(db_user_refresh_token)
    db.commit()
    db.refresh(db_user_refresh_token)
    return db_user_refresh_token


def delete_user_refresh_token(db: Session, user_id: int | Column[Integer], refresh_token: str | Column[String]):
    db.query(models.UserRefreshToken).filter(
        models.UserRefreshToken.id_user == user_id,
        models.UserRefreshToken.refresh_token == refresh_token
        ).delete()
    db.commit()


def delete_all_user_refresh_token(db: Session, user_id: int | Column[Integer]):
    db.query(models.UserRefreshToken).filter(models.UserRefreshToken.id_user == user_id).delete()
    db.commit()


def create_user_white_ip(db: Session, user_id: int | Column[Integer], white_ip: str | Column[String]) -> models.UserWhiteIP:
    db_user_white_ip = models.UserWhiteIP(
        id_user = user_id,
        white_ip = white_ip
    )
    db.add(db_user_white_ip)
    db.commit()
    db.refresh(db_user_white_ip)
    return db_user_white_ip


def get_tasks_by_user_id(db: Session, user_id: int):
    result = db.execute(select(models.TimetableUser).where(models.TimetableUser.id_user == user_id))
    tables = []
    for res in result:
        tables.append(res.TimetableUser.id_timetable)
    tasks = []
    for i in tables:
        tasks.append(get_all_tasks_in_table(db, i))
    return tasks


def get_task_id(subject: str, description: str, id_timetable: int, db: Session):
    result = db.execute(select(models.Task).where(models.Task.subject == subject). where(models.Task.id_timetable
                                                                                         == id_timetable).
                        where(models.Task.description == description))
    res = result.scalars().all()
    return res[0].id


def create_task(db: Session, task: schemas.TaskOut, user_id: int):
    db_task = models.Task(
        id_timetable=task.timetable_id,
        description=task.description,
        deadline=task.deadline,
        subject=task.subject
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    id_task = get_task_id(task.subject, task.description, task.timetable_id, db)
    db_statuses = models.TaskStatuses(
        id_task=id_task,
        id_user=user_id,
        status=task.statuses[0].status
    )
    db.add(db_statuses)
    db.commit()
    db.refresh(db_statuses)
    return db_task


def get_timetables(
    db: Session,
    timetable_name: str | Column[String],
    university_id: int | Column[Integer],
    specialization_id: int | Column[Integer],
    course: int | Column[Integer],
    skip: int,
    limit: int,
) -> list[models.Timetable] | None:
    return db.query(models.Timetable).filter(
        models.Timetable.name == timetable_name,
        models.Timetable.id_university == university_id,
        models.Timetable.id_specialization == specialization_id,
        models.Timetable.course == course,
    ).offset(skip).limit(limit).all()


def get_timetable_by_name_and_user_id(
    db: Session,
    timetable_name: str | Column[String],
    user_id: int | Column[Integer],
    ) -> models.Timetable | None:
    return db.query(models.Timetable).join(
        models.TimetableUser,
        models.TimetableUser.id_user == user_id
        ).filter(models.Timetable.name == timetable_name).first()


def get_timetable_by_id(db: Session, timetable_id: int | Column[Integer]) -> models.Timetable | None:
    return db.query(models.Timetable).filter(models.Timetable.id == timetable_id).first()


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


def get_timetables_id_where_user_is_elder(db: Session, user_id: int | Column[Integer]) -> list[int] | None:
    timetables_id = db.query(models.TimetableUser.id_timetable).filter(
        models.TimetableUser.id_user == user_id,
        models.TimetableUser.status == schemas.TimetableUserStatuses.elder,
    ).all()
    return [timetable_id[0] for timetable_id in timetables_id]


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


def create_timetable_user(db: Session, timetable_user_relation: schemas.TimetableUserCreate):
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
) -> models.Specialization | None:
    return db.query(models.Specialization).filter(
        models.Specialization.code == specialization_code,
        ).first()


def get_specialization_by_id(db: Session, specialization_id: int | Column[Integer]) -> models.Specialization | None:
    return db.query(models.Specialization).filter(models.Specialization.id == specialization_id).first()


def create_upper_weekly_timetable(
    db: Session, 
    timetable_id: int | Column[Integer], 
    upper_weekly_timetable: list[schemas.WeekCreate]
    ):
    for upper_daily_timetable in upper_weekly_timetable:
        create_upper_week_day(db, timetable_id, upper_daily_timetable)
    

def create_upper_week_day(
    db: Session, 
    timetable_id: int | Column[Integer], 
    upper_daily_timetable: schemas.WeekCreate
):
    upper_day = create_day_in_upper_week(db, timetable_id, upper_daily_timetable.day)
    for upper_day_subject in upper_daily_timetable.subjects:
        create_upper_day_subject(db, upper_day.id, upper_day_subject)


def create_day_in_upper_week(db: Session, timetable_id: int | Column[Integer], day: schemas.Day) -> models.UpperWeek:
    db_upper_week = models.UpperWeek(
        id_timetable = timetable_id,
        day = day,
    )
    db.add(db_upper_week)
    db.commit()
    db.refresh(db_upper_week)
    return db_upper_week


def create_upper_day_subject(
    db: Session,
    upper_day_id: int | Column[Integer],
    upper_day_subject: schemas.DaySubjectsBase
):
    db_upper_day_subject = models.UpperDaySubjects(
        id_upper_week = upper_day_id,
        subject = upper_day_subject.subject,
        start_time = upper_day_subject.start_time,
        end_time = upper_day_subject.end_time
    )
    db.add(db_upper_day_subject)
    db.commit()


def update_upper_weekly_timetable(db: Session, upper_weekly_timetable: list[schemas.WeekUpdate]):
    for upper_day_timetable in upper_weekly_timetable:
        update_day_in_upper_week(db, upper_day_timetable.day, upper_day_timetable.id)
        for upper_day_subject in upper_day_timetable.subjects:
            update_upper_day_subject(db, upper_day_subject)


def update_day_in_upper_week(db: Session, day: schemas.Day, day_id: int | Column[Integer]):
    db.query(models.UpperWeek).filter(models.UpperWeek.id == day_id).update(
        {
            models.UpperWeek.day: day
        },
        synchronize_session=False
    )
    db.commit()


def update_upper_day_subject(
    db: Session,
    upper_day_subject: schemas.DaySubjects
):
    db.query(models.UpperDaySubjects).filter(models.UpperDaySubjects.id == upper_day_subject.id).update(
        {
            models.UpperDaySubjects.subject: upper_day_subject.subject,
            models.UpperDaySubjects.start_time: upper_day_subject.start_time,
            models.UpperDaySubjects.end_time: upper_day_subject.end_time
        },
        synchronize_session=False
    )
    db.commit()


def delete_upper_weekly_timetable(db: Session, timetable_id: int | Column[Integer]):
    db.query(models.UpperWeek).filter(models.UpperWeek.id_timetable == timetable_id).delete()
    db.commit()


def delete_upper_daily_timetable(db: Session, day_id: int | Column[Integer]):
    db.query(models.UpperWeek).filter(models.UpperWeek.id == day_id).delete()
    db.commit()


def delete_upper_day_subject(db: Session, subject_id: int | Column[Integer]):
    db.query(models.UpperDaySubjects).filter(models.UpperDaySubjects.id == subject_id).delete()
    db.commit()


def create_lower_weekly_timetable(
    db: Session, 
    timetable_id: int | Column[Integer], 
    lower_weekly_timetable: list[schemas.WeekCreate]
    ):
    for lower_daily_timetable in lower_weekly_timetable:
        create_lower_week_day(db, timetable_id, lower_daily_timetable)
    

def create_lower_week_day(
    db: Session, 
    timetable_id: int | Column[Integer], 
    lower_daily_timetable: schemas.WeekCreate
):
    lower_day = create_day_in_lower_week(db, timetable_id, lower_daily_timetable.day)
    for lower_day_subject in lower_daily_timetable.subjects:
        create_lower_day_subject(db, lower_day.id, lower_day_subject)


def create_day_in_lower_week(db: Session, timetable_id: int | Column[Integer], day: schemas.Day) -> models.LowerWeek:
    db_lower_week = models.LowerWeek(
        id_timetable = timetable_id,
        day = day,
    )
    db.add(db_lower_week)
    db.commit()
    db.refresh(db_lower_week)
    return db_lower_week


def create_lower_day_subject(
    db: Session,
    lower_day_id: int | Column[Integer],
    lower_day_subject: schemas.DaySubjectsBase
    ) -> models.UpperDaySubjects:
    db_lower_day_subject = models.LowerDaySubjects(
        id_lower_week = lower_day_id,
        subject = lower_day_subject.subject,
        start_time = lower_day_subject.start_time,
        end_time = lower_day_subject.end_time
    )
    db.add(db_lower_day_subject)
    db.commit()
    db.refresh(db_lower_day_subject)
    return db_lower_day_subject


def update_lower_weekly_timetable(db: Session, lower_weekly_timetable: list[schemas.WeekUpdate]):
    for lower_day_timetable in lower_weekly_timetable:
        update_day_in_lower_week(db, lower_day_timetable.day, lower_day_timetable.id)
        for lower_day_subject in lower_day_timetable.subjects:
            update_lower_day_subject(db, lower_day_subject)


def update_day_in_lower_week(db: Session, day: schemas.Day, day_id: int | Column[Integer]):
    db.query(models.LowerWeek).filter(models.LowerWeek.id == day_id).update(
        {
            models.LowerWeek.day: day
        },
        synchronize_session=False
    )
    db.commit()


def update_lower_day_subject(
    db: Session,
    lower_day_subject: schemas.DaySubjects
):
    db.query(models.LowerDaySubjects).filter(models.LowerDaySubjects.id == lower_day_subject.id).update(
        {
            models.LowerDaySubjects.subject: lower_day_subject.subject,
            models.LowerDaySubjects.start_time: lower_day_subject.start_time,
            models.LowerDaySubjects.end_time: lower_day_subject.end_time
        },
        synchronize_session=False
    )
    db.commit()


def delete_lower_weekly_timetable(db: Session, timetable_id: int | Column[Integer]):
    db.query(models.LowerWeek).filter(models.LowerWeek.id_timetable == timetable_id).delete()
    db.commit()


def delete_lower_daily_timetable(db: Session, day_id: int | Column[Integer]):
    db.query(models.LowerWeek).filter(models.LowerWeek.id == day_id).delete()
    db.commit()


def delete_lower_day_subject(db: Session, subject_id: int | Column[Integer]):
    db.query(models.LowerDaySubjects).filter(models.LowerDaySubjects.id == subject_id).delete()
    db.commit()


def get_timetable_user_status(db: Session, user_id: int | Column[Integer], timetable_id: int | Column[Integer]) -> schemas.TimetableUserStatuses:
    return db.query(models.TimetableUser.status).filter(
        models.TimetableUser.id_user == user_id,
        models.TimetableUser.id_timetable == timetable_id,
        ).first()[0] # type: ignore


def get_timetable_elder(db: Session, timetable_id: int | Column[Integer]) -> int | None:
    return db.query(models.TimetableUser.id_user).filter(
        models.TimetableUser.id_timetable == timetable_id,
        models.TimetableUser.status == schemas.TimetableUserStatuses.elder
    ).first()[0]  # type: ignore


def create_application(db: Session, user_id: int| Column[Integer], timetable_id: int | Column[Integer]):
    application = models.Application(
        id_user = user_id,
        id_timetable = timetable_id
    )
    db.add(application)
    db.commit()


def get_timetable_users_relation_by_user_id(db: Session, user_id: int | Column[Integer]) -> list[models.TimetableUser] | list[None]:
    return db.query(models.TimetableUser).filter(
        models.TimetableUser.id_user == user_id,
        ).all()


def get_timetable_user_relation_by_user_id_and_timetable_id(
    db: Session, 
    user_id: int | Column[Integer], 
    timetable_id: int | Column[Integer]
) -> models.TimetableUser | None:
    return db.query(models.TimetableUser).filter(
        models.TimetableUser.id_user == user_id,
        models.TimetableUser.id_timetable == timetable_id,
        ).first()


def create_timetable_user_relation(db: Session, user_id: int | Column[Integer], timetable_id: int | Column[Integer]):
    timetable_user_relation = models.TimetableUser(
        id_user = user_id,
        id_timetable = timetable_id,
        status = schemas.TimetableUserStatuses.user,
    )
    db.add(timetable_user_relation)
    db.commit()


def delete_timetable_user_relation(db: Session, user_id: int | Column[Integer], timetable_id: int | Column[Integer]):
    db.query(models.TimetableUser).filter(
        models.TimetableUser.id_user == user_id,
        models.TimetableUser.id_timetable == timetable_id
    ).delete()
    db.commit()

    
def get_application_by_id(db: Session, application_id: int | Column[Integer]) -> models.Application | None:
    return db.query(models.Application).filter(models.Application.id ==application_id).first()


def get_applications_by_timetable_id(db: Session, timetable_id: int | Column[Integer]) -> list[models.Application] | list[None]:
    return db.query(models.Application).filter(models.Application.id_timetable == timetable_id).all()

def get_application_by_user_id_and_timetable_id(
    db: Session, user_id: int | Column[Integer],
    timetable_id: int | Column[Integer]
) -> models.Application | None:
    return db.query(models.Application).filter(
        models.Application.id_user == user_id,
        models.Application.id_timetable == timetable_id,
    ).first()


def delete_application(db: Session, application_id: int | Column[Integer]):
    db.query(models.Application).filter(models.Application.id == application_id).delete()
    db.commit()


def update_timetable(db: Session, timetable_id: int | Column[Integer], timetable_data: schemas.TimetableCreate):
    db.query(models.Timetable).filter(models.Timetable.id == timetable_id).update(
        {
            models.Timetable.name: timetable_data.name,
            models.Timetable.id_university: timetable_data.id_university,
            models.Timetable.id_specialization: timetable_data.id_specialization,
            models.Timetable.course: timetable_data.course
        },
        synchronize_session=False
        )
    db.commit()  


def delete_timetable(db: Session, timetable_id: int | Column[Integer]):
    db.query(models.Timetable).filter(models.Timetable.id == timetable_id).delete()
    db.commit()


def get_task_by_subject(db: Session, id_timetable: int, subject: str):
    result = db.execute(select(models.Task).where(models.Task.subject == subject).where(models.Task.id_timetable ==
                                                                                        id_timetable))
    return result.scalars().all()


def get_all_tasks_in_table(db: Session, id_timetable: int, user_id: int):
    result = db.execute(select(models.Task).where(models.Task.id_timetable == id_timetable))
    tasks = result.scalars().all()
    result = db.execute(select(models.TaskStatuses).where(models.TaskStatuses.id_user == user_id))
    statuses = result.scalars().all()
    tas = []
    for task in tasks:
        i = 0
        for stat in statuses:
            if stat.id_task == task.id:
                i = 1
                stats = [{
                    "id": stat.id_task,
                    "id_user": user_id,
                    "status": stat.status
                }]
                break
        if i == 1:
            t = {
                "id": task.id,
                "timetable_id": id_timetable,
                "description": task.description,
                "deadline": task.deadline,
                "subject": task.subject,
                "statuses": stats
            }
            tas.append(t)
            i = 0
    return tas


def delete_task_from_table(db: Session, id_timetable: int, id_task: int):
    db.query(models.Task).filter(models.Task.id == id_task).filter(models.Task.id_timetable == id_timetable).delete()
    db.commit()
    return 'Task deleted successfully'
