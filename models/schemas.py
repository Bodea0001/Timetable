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
    id: int
    day: Day

    class Config:
        orm_mode = True


class Week(WeekBase):
    id_timetable: int


class DaySubjects(BaseModel):
    id: int
    subject: str
    start_time: time
    end_time: time

    class Config:
        orm_mode = True


class UpperWeekOut(WeekBase):
    subjects: list[DaySubjects]


class LowerWeekOut(WeekBase):
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


class TimetableOut(TimetableOutLite):
    id: int
    
    upper_week_items: list[UpperWeek]
    lower_week_items: list[LowerWeek]
    tasks: list[Task]


class Timetable(TimetableBase):
    id: int
    id_university: int
    id_specialization: int

    upper_week_items: list[UpperWeek]
    lower_week_items: list[LowerWeek]
    tasks: list[Task]


class TimetableUserStatuses(str, Enum):
    elder = "староста"
    user = "пользователь"   


class TimetableUser(BaseModel):
    id_user: int
    id_timetable: int
    status: TimetableUserStatuses


class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str

    class Config:
        orm_mode = True


class UserOutLite(UserBase):
    id: int
    timetables_info: list[TimetableOutLite]


class UserOut(UserBase):
    id: int
    timetables_info: list[TimetableOut]


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    registry_date: datetime
    tg_username: str | None = None
    timetables_info: list[Timetable]


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
        course: int = Form(ge=1, le=5)
    ):
        self.name = name
        self.university = university
        self.specialization_name = specialization_name
        self.specialization_code = specialization_code
        self.education_level = education_level
        self.course = course