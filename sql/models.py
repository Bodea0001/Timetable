from sqlalchemy import Column, Integer, String, Text, DateTime, Time, ForeignKey
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


class University(Base): # type: ignore
    __tablename__ = "university"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)


class Specialization(Base): # type: ignore
    __tablename__ = "specialization"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), nullable=False)
    name = Column(String, nullable=False)


class Task(Base): # type: ignore
    __tablename__ = "task"

    id = Column(Integer, primary_key=True, index=True)
    id_timetable = Column(ForeignKey("timetable.id"))
    description = Column(Text, nullable=False)
    deadline = Column(DateTime, nullable=False)

    statuses = relationship("TaskStatuses", back_populates="owner")


class TaskStatuses(Base): # type: ignore
    __tablename__ = "task_statuses"

    id = Column(Integer, primary_key=True, index=True)
    id_task = Column(ForeignKey("task.id"))
    id_user = Column(ForeignKey("user.id"))
    status = Column(String, nullable=False)

    owner = relationship("Task", back_populates="statuses")


class UpperWeek(Base): # type: ignore
    __tablename__ = "upper_week"

    id = Column(Integer, primary_key=True, index=True)
    id_timetable = Column(ForeignKey("timetable.id"))
    subject = Column(String(150), nullable=False)
    day = Column(String, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)


class LowerWeek(Base): # type: ignore
    __tablename__ = "lower_week"

    id = Column(Integer, primary_key=True, index=True)
    id_timetable = Column(ForeignKey("timetable.id"))
    subject = Column(String(150), nullable=False)
    day = Column(String, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)


class Timetable(Base): # type: ignore
    __tablename__ = "timetable"

    id = Column(Integer, primary_key=True, index=True)
    id_university = Column(ForeignKey("university.id"))
    id_spesialization = Column(ForeignKey("specialization.id"))
    education_level = Column(String(50), nullable=False)
    course = Column(Integer, nullable=False)
    id_user = Column(ForeignKey("user.id"))
    status = Column(String(50))

    upper_week_items = relationship("UpperWeek")
    lower_week_items = relationship("LowerWeek")
    tasks = relationship("Task")


def create_db_and_tables():
    Base.metadata.create_all(engine)  # type: ignore

if __name__=="__main__":
    create_db_and_tables()