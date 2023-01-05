from pydantic import BaseModel, EmailStr
from fastapi import Form
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, time
from enum import Enum


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenData(BaseModel):
    username: str


class University(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class Education_level(str, Enum):
    undergraduate = "Бакалавриат"
    magistracy = "Магистратура"
    specialty = "Специалитет"


class Specialization(BaseModel):
    id: int
    code: str
    name: str
    education_level: Education_level

    class Config:
        orm_mode = True


class TaskStatusesEnum(str, Enum):
    in_progress = "В процессе"
    complited = "Завершено"


class TaskStatusesBase(BaseModel):
    id: int
    id_user: int
    status: TaskStatusesEnum


class TaskStatuses(TaskStatusesBase):
    id_task: int


# Task Base Nodel
class TaskBase(BaseModel):
    id: int
    timetable_id: int
    description: str
    deadline: datetime
    subject: str

    class Config:
        orm_mode = True


# Task Out Model inherit from TaskBase
class TaskOut(TaskBase):
    statuses: list[TaskStatusesBase]


class Task(TaskBase):
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


class DaySubjects(DaySubjectsBase):
    id: int


class WeekCreate(WeekBase):
    subjects: list[DaySubjectsBase]


class WeekOut(Week):
    subjects: list[DaySubjects]


class UpperDaySubjects(DaySubjects):
    id_upper_week: int


class UpperWeek(Week):
    subjects: list[UpperDaySubjects]


class LowerDaySubjects(DaySubjects):
    id_lower_week: int


class LowerWeek(Week):
    subjects: list[LowerDaySubjects]


class TimetableBase(BaseModel):
    name: str
    course: int

    class Config:
        orm_mode = True 


class TimetableCreate(TimetableBase):
    id_university: int
    id_specialization: int


class TimetableOutLite(TimetableBase):
    id: int
    university: str
    specialization_name: str
    specialization_code: str
    education_level: Education_level
    creation_date: datetime


class TimetableOut(TimetableOutLite):
    id: int
    
    upper_week_items: list[UpperWeek]
    lower_week_items: list[LowerWeek]
    tasks: list[Task]


class Timetable(TimetableBase):
    id: int
    id_university: int
    id_specialization: int
    creation_date: datetime

    upper_week_items: list[UpperWeek]
    lower_week_items: list[LowerWeek]
    tasks: list[Task]


class TimetableUserStatuses(str, Enum):
    elder = "староста"
    user = "пользователь"   


class TimetableUserCreate(BaseModel):
    id_user: int
    id_timetable: int
    status: TimetableUserStatuses


class TimetableUser(TimetableUserCreate):
    date_added: datetime
    

class ApplicationBase(BaseModel):
    id: int
    id_timetable: int
    creation_date: datetime


class Application(ApplicationBase):
    id_user: int


class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str

    class Config:
        orm_mode = True


class UserOutLite(UserBase):
    id: int
    applications: list[ApplicationBase]
    timetables_info: list[TimetableOutLite]


class UserOut(UserBase):
    id: int
    applications: list[ApplicationBase]
    timetables_info: list[TimetableOut]


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    registry_date: datetime
    tg_username: str | None = None
    applications: list[ApplicationBase]
    refresh_tokens: list[str]
    white_list_ip: list[str]
    timetables_info: list[Timetable]

class UserRefreshToken(BaseModel):
    id: int
    id_user: int
    refresh_token: str


class UserWhiteIP(BaseModel):
    id: int
    id_user: int
    white_ip: str


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
        education_level: Education_level | None = Form(default=None),
        course: int = Form(ge=1, le=5)
    ):
        self.name = name
        self.university = university
        self.specialization_name = specialization_name
        self.specialization_code = specialization_code
        self.education_level = education_level
        self.course = course