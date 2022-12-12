import sys
from sqlalchemy import Column, Integer, String, Text, DateTime, Time, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime

from sql.database import Base, engine


class User(Base):  # type: ignore
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password = Column(String(150), nullable=False)
    first_name = Column(String(150), nullable=False)
    last_name = Column(String(150), nullable=False)
    registry_date = Column(DateTime, default=datetime.utcnow())
    tg_username = Column(String)

    timetables_info = relationship("Timetable", secondary="timetable_user", back_populates="users_info")


class University(Base): # type: ignore
    __tablename__ = "university"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)


class Specialization(Base): # type: ignore
    __tablename__ = "specialization"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), nullable=False, unique=True)
    name = Column(String, nullable=False)
    education_level = Column(String(20), nullable=False)


class Task(Base): # type: ignore
    __tablename__ = "task"

    id = Column(Integer, primary_key=True, index=True)
    id_timetable = Column(ForeignKey("timetable.id"))
    description = Column(Text, nullable=False)
    subject = Column(String(150))
    deadline = Column(DateTime, nullable=False)

    statuses = relationship("TaskStatuses")
    # owner = relationship("Timetable", back_populates="tasks")


class TaskStatuses(Base): # type: ignore
    __tablename__ = "task_statuses"

    id = Column(Integer, primary_key=True, index=True)
    id_task = Column(ForeignKey("task.id"))
    id_user = Column(ForeignKey("user.id"))
    status = Column(String, nullable=False)
    # owner = relationship("Task", back_populates="statuses")


class UpperWeek(Base): # type: ignore
    __tablename__ = "upper_week"

    id = Column(Integer, primary_key=True, index=True)
    id_timetable = Column(ForeignKey("timetable.id"))
    day = Column(String, nullable=False)

    subjects = relationship("UpperDaySubjects")
    # owner = relationship("Timetable", back_populates="upper_week_items")


class UpperDaySubjects(Base): # type: ignore
    __tablename__ = "upper_day_subjects"
    
    id = Column(Integer, primary_key=True, index=True)
    id_upper_week = Column(ForeignKey("upper_week.id"))
    subject = Column(String(150), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    # owner = relationship("UpperWeek", back_populates="subjects")


class LowerWeek(Base): # type: ignore
    __tablename__ = "lower_week"

    id = Column(Integer, primary_key=True, index=True)
    id_timetable = Column(ForeignKey("timetable.id"))
    day = Column(String, nullable=False)

    subjects = relationship("LowerDaySubjects")
    # owner = relationship("Timetable", back_populates="lower_week_items")


class LowerDaySubjects(Base): # type: ignore
    __tablename__ = "lower_day_subjects"
    id = Column(Integer, primary_key=True, index=True)
    id_lower_week = Column(ForeignKey("lower_week.id"), nullable=False)
    subject = Column(String(150), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    # owner = relationship("LowerWeek", back_populates="subjects")


class Timetable(Base): # type: ignore
    __tablename__ = "timetable"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    id_university = Column(ForeignKey("university.id"), nullable=False)
    id_specialization = Column(ForeignKey("specialization.id"), nullable=False)
    course = Column(Integer, nullable=False)

    upper_week_items = relationship("UpperWeek")
    lower_week_items = relationship("LowerWeek")
    tasks = relationship("Task")
    users_info = relationship("User", secondary="timetable_user", back_populates="timetables_info")


class  TimetableUser(Base):  #type: ignore
    __tablename__ = "timetable_user"

    id_user = Column(ForeignKey("user.id"), primary_key=True, index=True)
    id_timetable = Column(ForeignKey("timetable.id"), primary_key=True, index=True)
    status = Column(String(50), nullable=False)


def create_db_and_tables():
    Base.metadata.create_all(engine)  # type: ignore


def drop_tables():
    Base.metadata.drop_all(engine) # type: ignore
    

if __name__=="__main__":
    if sys.argv[1] == 'createdb':
        create_db_and_tables()
    elif sys.argv[1] == 'dropdb':
        drop_tables()