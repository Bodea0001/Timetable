from pydantic import BaseModel, EmailStr
from fastapi import Form
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, time
from enum import Enum


class AccessToken(BaseModel):
    access_token: str
    access_token_expires: int


class RefreshToken(BaseModel):
    refresh_token: str
    refresh_token_expires: int


class Token(AccessToken, RefreshToken):
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
    id_timetable: int
    description: str
    deadline: datetime
    subject: str

    class Config:
        orm_mode = True


class TaskTags(str, Enum):
    one = "один"
    all = "все"


class TaskUpdate(TaskBase):
    id: int

    
# Task Out Model inherit from TaskBase
class TaskOutForUser(TaskBase):
    id: int
    tag: TaskTags
    status: TaskStatusesEnum
    creation_date: datetime


class TaskStatusesOut(TaskStatusesBase):
    user_email: EmailStr
    user_first_name: str
    user_last_name: str


class TaskOutForElder(TaskBase):
    id: int
    tag: TaskTags
    statuses: list[TaskStatusesOut]
    creation_date: datetime


class Task(TaskBase):
    id: int
    tag: TaskTags
    statuses: list[TaskStatuses]
    creation_date: datetime


class Day(str, Enum):
    MONDAY = "Понедельник"
    TUESDAY = "Вторник"
    WEDNESDAY = "Среда"
    THURSDAY = "Четверг"
    FRIDAY = "Пятница"
    SATURDAY = "Суббота"
    SUNDAY = "Воскресенье"


class WeekBase(BaseModel):
    day: Day

    class Config:
        orm_mode = True


class WeekName(str, Enum):
    UPPER = "верхняя"
    LOWER = "нижняя"


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


class WeekUpdate(WeekBase):
    id: int
    subjects: list[DaySubjects]


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


class TimetableUserStatuses(str, Enum):
    elder = "староста"
    user = "пользователь"   


class TimetableOut(TimetableOutLite):
    id: int
    user_status: TimetableUserStatuses
    
    upper_week_items: list[UpperWeek]
    lower_week_items: list[LowerWeek]
    tasks: list[TaskOutForUser]


class Timetable(TimetableBase):
    id: int
    id_university: int
    id_specialization: int
    creation_date: datetime

    upper_week_items: list[UpperWeek]
    lower_week_items: list[LowerWeek]
    tasks: list[Task]


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


class ApplicationOut(ApplicationBase):
    user_email: str
    user_first_name: str
    user_last_name: str

class ApplicationOutForUser(ApplicationBase):
    timetable_name: str
    timetable_university: str
    timetable_specialization_name: str
    timetable_specialization_code: str
    timetable_education_level: Education_level
    timetable_course: int


class UserUpdate(BaseModel):
    first_name: str
    last_name: str


class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str

    class Config:
        orm_mode = True


class UserOutLite(UserBase):
    id: int
    tg_user_id: int | None = None
    applications: list[ApplicationBase]
    timetables_info: list[TimetableOutLite]


class UserOut(UserBase):
    id: int
    tg_user_id: int | None = None
    applications: list[ApplicationOutForUser]
    timetables_info: list[TimetableOut]


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    registry_date: datetime
    tg_user_id: int | None = None
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


class PassChangeRequestBase(BaseModel):
    id: int
    email: EmailStr


class PassChangeRequest(PassChangeRequestBase):
    new_password: str
    creation_date: datetime


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

    
class ChangePasswordForm:
    def __init__(
        self,
        email: EmailStr = Form(),
        new_password: str = Form(),
    ):
        self.email = email
        self.new_password = new_password