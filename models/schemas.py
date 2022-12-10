from pydantic import BaseModel, EmailStr
from fastapi import Form
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, time
from enum import Enum


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str


class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str


class UserOut(UserBase):
    id: int


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    registry_date: datetime
    tg_username: str | None = None

    class Config:
        orm_mode = True


class University(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class Specialization(BaseModel):
    id: int
    code: str
    name: str

    class Config:
        orm_mode = True


class TaskStatusesEnum(str, Enum):
    in_progress = "В процессе"
    complited = "Завершено"


class TaskStatusesBase(BaseModel):
    id_user: int
    status: TaskStatusesEnum


class TaskStatuses(TaskStatusesBase):
    id: int
    id_task: int


# Task Base Nodel
class TaskBase(BaseModel):
    timetable_id: int
    description: str
    deadline: datetime
    subject: str | None = None

    class Config:
        orm_mode = True


# Task Out Model inherit from TaskBase
class TaskOut(TaskBase):
    statuses: list[TaskStatusesBase]


class Task(TaskBase):
    id: int
    statuses: list[TaskStatuses]


class Day(str, Enum):
    monday = "Понедельник"
    tuesday = "Вторник"
    wednesday = "Среда"
    thursday = "Четверг"
    friday = "Пятница"
    saturday = "Суббота"
    sunday = "Воскресенье"


class WeekBase(BaseModel):
    day: Day

    class Config:
        orm_mode = True


class Week(WeekBase):
    id: int
    id_timetable: int


class DaySubjectsBase(BaseModel):
    subject: str
    start_time: time
    end_time: time

    class Config:
        orm_mode = True


class DaySubjectsOut(DaySubjectsBase):
    pass


class UpperWeekOut(WeekBase):
    subjects: list[DaySubjectsOut]


class LowerWeekOut(WeekBase):
    subjects: list[DaySubjectsOut]


class DaySubjects(DaySubjectsBase):
    id: int


class UpperDaySubjects(DaySubjects):
    id_upper_week: int


class UpperWeek(Week):
    subjects: list[UpperDaySubjects]


class LowerDaySubjects(DaySubjects):
    id_lower_week: int


class LowerWeek(Week):
    subjects: list[LowerDaySubjects]


class Education_level(str, Enum):
    undergraduate = "Бакалавриат"
    magistracy = "Магистратура"
    specialty = "Специалитет"
    postgraduate = "Аспирантура"


class TimetableBase(BaseModel):
    name: str
    education_level: Education_level
    course: int
    id_user: int

    class Config:
        orm_mode = True 


class TimetableStatuses(str, Enum):
    elder = "староста"
    user = "пользователь"   


class TimetableCreate(TimetableBase):
    id_university: int
    id_specialization: int
    status: TimetableStatuses


class TimetableOut(TimetableBase):
    university: str
    specialization_name: str
    specialization_code: str
    status: TimetableStatuses

    upper_week_items: list[UpperWeekOut]
    lower_week_items: list[LowerWeekOut]
    tasks: list[TaskOut]


class Timetable(TimetableBase):
    id: int
    id_university: int
    id_specialization: int
    status: TimetableStatuses

    upper_week_items: list[UpperWeek]
    lower_week_items: list[LowerWeek]
    tasks: list[Task]


class OAuth2PasswordRequestFormUpdate(OAuth2PasswordRequestForm):
    def __init__(
        self,
        grant_type: str = Form(default=None, regex="password"),
        username: str = Form(),
        password: str = Form(),
        scope: str = Form(default=""),
        client_id: str | None = Form(default=None),
        client_secret: str | None = Form(default=None),
        first_name: str = Form(),
        last_name: str = Form(),
    ):
        super().__init__(
            grant_type=grant_type,
            username=username,
            password=password,
            scope=scope,
            client_id=client_id,
            client_secret=client_secret,
        )
        self.first_name = first_name
        self.last_name = last_name


class TimetableRequestForm:
    def __init__(
        self,
        name: str = Form(),
        university: str = Form(),
        specialization_name: str | None= Form(default=None),
        specialization_code: str | None = Form(default=None),
        education_level: Education_level = Form(),
        course: int = Form(ge=1, le=5),
        status: TimetableStatuses | None = Form(default=None)
    ):
        self.name = name
        self.university = university
        self.specialization_name = specialization_name
        self.specialization_code = specialization_code
        self.education_level = education_level
        self.course = course
        self.status = status