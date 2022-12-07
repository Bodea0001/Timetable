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
    overdue = "Просрочено"


class TaskStatuses(BaseModel):
    id: int
    id_task: int
    id_user: int
    status: TaskStatusesEnum


class Task(BaseModel):
    id: int
    description: str
    time: datetime
    statuses: list[TaskStatuses]

    class Config:
        orm_mode = True


class Day(str, Enum):
    monday = "Понедельник"
    tuesday = "Вторник"
    wednesday = "Среда"
    thursday = "Четверг"
    friday = "Пятница"
    saturday = "Суббота"
    sunday = "Воскресенье"


class Week(BaseModel):
    id: int
    subject: str
    day: Day
    start_time: time
    end_time: time

    class Config:
        orm_mode = True


class UpperWeek(Week):

    class Config:
        orm_mode = True


class LowerWeek(Week):
    
    class Config:
        orm_mode = True


class Education_level(str, Enum):
    undergraduate = "Бакалавриат"
    magistracy = "Магистратура"
    specialty = "Специалитет"
    postgraduate = "Аспирантура"


class TimetableStatuses(str, Enum):
    admin = "админ"
    elder = "староста"
    user = "пользователь"


class Timetable:
    id: int
    name: str
    id_university: int
    id_specialization: int
    education_level: Education_level
    course: int
    id_user: int
    status: TimetableStatuses

    upper_week_items: list[UpperWeek]
    lower_week_items: list[LowerWeek]
    tasks: list[Task]

    class Config:
        orm_mode = True 


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