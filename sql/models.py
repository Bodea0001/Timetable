import sys
from sqlalchemy import Column, Integer, String, Text, DateTime, Time, ForeignKey, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

from sql.database import engine


Base = declarative_base()


class User(Base):  # type: ignore
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password = Column(String(150), nullable=False)
    first_name = Column(String(150), nullable=False)
    last_name = Column(String(150), nullable=False)
    registry_date = Column(DateTime, default=datetime.utcnow())
    tg_user_id = Column(BigInteger)

    applications = relationship("Application")
    refresh_tokens = relationship("UserRefreshToken")
    white_list_ip = relationship("UserWhiteIP")
    timetables_info = relationship("Timetable", secondary="timetable_user", back_populates="users_info")


class PassChangeRequest(Base):  # type: ignore
    __tablename__ = "pass_change_request"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(150), nullable=False)
    new_password = Column(String(150), nullable=False)
    creation_date = Column(DateTime, default=datetime.utcnow())


class Application(Base):  # type: ignore
    __tablename__ = "application"

    id = Column(Integer, primary_key=True, index=True)
    id_user = Column(ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    id_timetable = Column(ForeignKey("timetable.id", ondelete="CASCADE"), nullable=False)
    creation_date = Column(DateTime, default=datetime.utcnow())


class UserRefreshToken(Base):  # type: ignore
    __tablename__ = "user_refresh_token"

    id = Column(Integer, primary_key=True, index=True)
    id_user = Column(ForeignKey("user.id"), nullable=False)
    refresh_token = Column(String, nullable=False)


class UserWhiteIP(Base):  # type: ignore
    __tablename__ = "user_white_ip"

    id = Column(Integer, primary_key=True, index=True)
    id_user = Column(ForeignKey("user.id"), nullable=False)
    white_ip = Column(String(30), nullable=False)


class University(Base):  # type: ignore
    __tablename__ = "university"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)


class Specialization(Base):  # type: ignore
    __tablename__ = "specialization"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), nullable=False, unique=True)
    name = Column(String, nullable=False)
    education_level = Column(String(20), nullable=False)


class Task(Base):  # type: ignore
    __tablename__ = "task"

    id = Column(Integer, primary_key=True, index=True)
    id_timetable = Column(ForeignKey("timetable.id", ondelete="CASCADE"))
    id_creator = Column(ForeignKey("user.id", ondelete="CASCADE"))
    description = Column(Text, nullable=False)
    subject = Column(String(150))
    deadline = Column(DateTime, nullable=False)
    creation_date = Column(DateTime, default=datetime.utcnow())

    statuses = relationship("TaskStatuses", cascade="all, delete")


class TaskStatuses(Base):  # type: ignore
    __tablename__ = "task_statuses"

    id = Column(Integer, primary_key=True, index=True)
    id_task = Column(ForeignKey("task.id", ondelete="CASCADE"))
    id_user = Column(ForeignKey("user.id", ondelete="CASCADE"))
    status = Column(String, nullable=False)


class UpperWeek(Base):  # type: ignore
    __tablename__ = "upper_week"

    id = Column(Integer, primary_key=True, index=True)
    id_timetable = Column(ForeignKey("timetable.id", ondelete="CASCADE"))
    day = Column(String, nullable=False)

    subjects = relationship("UpperDaySubjects", cascade="all, delete")


class UpperDaySubjects(Base):  # type: ignore
    __tablename__ = "upper_day_subjects"
    
    id = Column(Integer, primary_key=True, index=True)
    id_upper_week = Column(ForeignKey("upper_week.id", ondelete="CASCADE"), nullable=False)
    subject = Column(String(150), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)


class LowerWeek(Base):  # type: ignore
    __tablename__ = "lower_week"

    id = Column(Integer, primary_key=True, index=True)
    id_timetable = Column(ForeignKey("timetable.id", ondelete="CASCADE"))
    day = Column(String, nullable=False)

    subjects = relationship("LowerDaySubjects", cascade="all, delete")


class LowerDaySubjects(Base):  # type: ignore
    __tablename__ = "lower_day_subjects"
    id = Column(Integer, primary_key=True, index=True)
    id_lower_week = Column(ForeignKey("lower_week.id", ondelete="CASCADE"), nullable=False)
    subject = Column(String(150), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)


class Timetable(Base):  # type: ignore
    __tablename__ = "timetable"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    id_university = Column(ForeignKey("university.id"))
    id_specialization = Column(ForeignKey("specialization.id"))
    course = Column(Integer)
    creation_date = Column(DateTime, default=datetime.utcnow())

    upper_week_items = relationship("UpperWeek", cascade="all, delete")
    lower_week_items = relationship("LowerWeek", cascade="all, delete")
    tasks = relationship("Task", cascade="all, delete")
    users_info = relationship("User", secondary="timetable_user", back_populates="timetables_info", cascade="all, delete")


class TimetableUser(Base):  # type: ignore
    __tablename__ = "timetable_user"

    id_user = Column(ForeignKey("user.id"), primary_key=True, index=True)
    id_timetable = Column(ForeignKey("timetable.id", ondelete="CASCADE"), primary_key=True, index=True)
    status = Column(String(50), nullable=False)
    date_added = Column(DateTime, default=datetime.utcnow())


def create_db_and_tables():
    Base.metadata.create_all(engine)  # type: ignore


def drop_tables():
    Base.metadata.drop_all(engine)  # type: ignore
    

if __name__ == "__main__":
    if sys.argv[1] == 'createdb':
        create_db_and_tables()
    elif sys.argv[1] == 'dropdb':
        drop_tables()
