from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer
from fastapi import HTTPException, status

from sql import models
from models.schemas import (
    TimetableOut,
    TimetableCreate,
    TimetableSearch,
    Education_level,
    TimetableOutLite,
    TimetableUserCreate,
    TimetableRequestForm,
    TimetableUserStatuses,
    UserPublicInformation,
    TimetableSearchRequestForm,
)
from crud.timetable import (
    create_timetable,
    get_timetable_by_id,
    update_timetable_data
)
from crud.specialization import (
    get_specialization_by_id,
    get_specialization_id_by_name,
    get_specialization_id_by_code,
)
from crud.timetable_user import (
    get_users_in_timetable,
    get_timetable_user_status,
    get_amount_of_user_timetables,
    create_timetable_user_relation,
)
from crud.university import (
    get_university_by_id,
    get_university_id_by_name_from_db
)
from controllers.week import (
    validate_upper_week_items,
    validate_lower_week_items
)
from controllers.task_controller import get_valid_tasks_in_timetable
from message import (
    INVALID_COURSE,
    UNIVERSITY_NOT_FOUND, 
    SPECIALIZATION_NOT_FOUND,
    EDUCATION_LEVEL_NOT_FOUND,
    SPEC_NAME_WIHTOUT_EDUC_LEVEL
)
from config import USER_TIMETABLES_LIMIT


def is_possible_to_add_new_timetable(
        db: Session, user_id: int | Column[Integer]) -> bool:
    """Проверяет, можно ли пользователю добавить еще одно расписание"""
    user_timetables_amount = get_amount_of_user_timetables(db, user_id)
    return user_timetables_amount < USER_TIMETABLES_LIMIT


def create_timetable_for_user(
        db: Session, data: TimetableCreate, user_id: int | Column[Integer],
        status: TimetableUserStatuses = TimetableUserStatuses.elder
    ) -> models.Timetable:
    """Создаёт расписание, которое потом добавляется к пользователю со статусом 
    "староста" (статус можно изменить)."""
    db_timetable = create_timetable(db, data)

    timetable_user_relation = TimetableUserCreate(
        id_user=user_id,  # type: ignore  
        id_timetable=db_timetable.id,  # type: ignore
        status=status)
    create_timetable_user_relation(db, timetable_user_relation)

    return db_timetable


def update_timetable(
        db: Session, timetable_id: int | Column[Integer], 
        timetable_data: TimetableCreate) -> models.Timetable:
    """Обновляет и возвращает расписание"""
    update_timetable_data(db, timetable_id, timetable_data)
    timetable = get_timetable_by_id(db, timetable_id)
    return timetable


def validate_timetable_data_to_create_or_update(
        db: Session, data: TimetableRequestForm) -> TimetableCreate:
    """Валидирует и отдает данные для создания или обновления расписания"""
    university_id = _get_university_id(db, data.university)
    specialization_id = _get_specialization_id(db, data.specialization_name, 
        data.specialization_code, data.education_level)

    _check_course(data.course)

    return TimetableCreate(
        name=data.name,
        course=data.course,
        id_university=university_id,
        id_specialization=specialization_id
    )


def _check_education_level(education_level: Education_level):
    """Проверяет, правильный ли уровень образования"""
    educ_levels = Education_level._value2member_map_.keys()
    if education_level not in educ_levels:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=EDUCATION_LEVEL_NOT_FOUND)


def _check_course(
        course: int, education_level: Education_level | None = None) -> None:
    """Проверяет, правильный ли курс"""
    if education_level:
        _check_education_level(education_level)

    if (not education_level and not 1 <= course <= 5 or 
    education_level == Education_level.undergraduate and not 1 <= course <= 4 or 
    education_level == Education_level.magistracy and not 1 <= course <= 2 or 
    education_level == Education_level.specialty and not 1 <= course <= 6):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=INVALID_COURSE)


def _get_university_id(
        db: Session, university_name: str | None) -> int | None:
    """Получает университет из БД и проверяет, есть ли университет с таким 
    наименованием. Если нету, то вызывает ошибку 404"""
    if not university_name:
        return None
    
    university_id = get_university_id_by_name_from_db(db, university_name)
    if not university_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=UNIVERSITY_NOT_FOUND)

    return university_id


def _get_university_name(university: models.University | None) -> str | None:
    return university.name if university else None # type: ignore


def _get_specialization_id(
        db: Session,
        specialization_name: str | None,
        specialization_code: str | None,
        education_level: Education_level | None) -> int| None:
    """Находит специальность в БД и отдает ее, если были введены данные. Если 
    данные введены неправильно, то вызывает ошибку 400. Если сами данные 
    неправильные, то вызывает ошибку 404"""
    if not any((specialization_name, specialization_code, education_level)):
        return None

    if specialization_name:
        if not education_level:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=SPEC_NAME_WIHTOUT_EDUC_LEVEL)

        _check_education_level(education_level)

        specialization_id = get_specialization_id_by_name(
            db, specialization_name, education_level)
    elif specialization_code:
        specialization_id = get_specialization_id_by_code(
            db, specialization_code)
    else:
        specialization_id = None

    if not specialization_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=SPECIALIZATION_NOT_FOUND)

    return specialization_id


def _get_specialization_data(
        spec: models.Specialization | None
    ) -> tuple[str, str, Education_level] | tuple[None, None, None]:
    """Возвращает данные специальности"""
    return (spec.name, spec.code, spec.education_level)  if spec else (None, None, None)  # type: ignore


def get_valid_timetables(
        db: Session, db_timetables: list[models.Timetable],
        user_id: int | Column[Integer]) -> list[TimetableOut]:
    """Возвращает валидные расписания"""
    return [get_valid_timetable(db, timetable, user_id)
            for timetable in db_timetables]


def get_valid_timetable(
        db: Session, db_timetable: models.Timetable,
        user_id: int | Column[Integer]) -> TimetableOut:
    """Возвращает валидное расписание"""
    user_status = get_timetable_user_status(db, user_id, db_timetable.id)
    if not user_status:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    university = get_university_by_id(db, db_timetable.id_university)  # type: ignore
    specialization = get_specialization_by_id(db, db_timetable.id_specialization) #type: ignore
    users = get_users_in_timetable(db, db_timetable.id)

    return validate_timetable(db, db_timetable, university, specialization, 
        user_id, user_status, users)
  

def validate_timetable(
        db: Session, 
        db_timetable: models.Timetable,
        university: models.University | None,
        specialization: models.Specialization | None,
        user_id: int | Column[Integer],
        status: TimetableUserStatuses,
        users: list[models.User]) -> TimetableOut:
    """Валидирует расписание"""
    univ_name = _get_university_name(university)
    spec_name, spec_code, educ_level = _get_specialization_data(specialization)
    valid_tasks = get_valid_tasks_in_timetable(db, db_timetable.id, user_id)

    valid_upper_week_items = validate_upper_week_items(db_timetable.upper_week_items)  # type: ignore
    valid_lower_week_items = validate_lower_week_items(db_timetable.lower_week_items)  # type: ignore

    valid_users = [_validate_public_info_about_user(user) for user in users]
    return TimetableOut(
        id=db_timetable.id, # type: ignore
        name=db_timetable.name, # type: ignore
        university=univ_name,
        specialization_name=spec_name, 
        specialization_code=spec_code, 
        education_level=educ_level, 
        course=db_timetable.course, # type: ignore
        user_status=status,
        creation_date=db_timetable.creation_date,  # type: ignore
        upper_week_items=valid_upper_week_items,
        lower_week_items=valid_lower_week_items,
        tasks=valid_tasks,
        users=valid_users # type: ignore
    )


def get_valid_timetables_lite(
        db: Session, timetables: list[models.Timetable]) -> list[TimetableOutLite]:
    """Возвращает упрощенные валидные расписания"""
    return [get_valid_timetable_lite(db, timetable)for timetable in timetables]


def get_valid_timetable_lite(
        db: Session, db_timetable: models.Timetable) -> TimetableOutLite:
    """Возвращает упрощенное валидное расписание"""
    university = get_university_by_id(db, db_timetable.id_university)  # type: ignore
    specialization = get_specialization_by_id(db, db_timetable.id_specialization) #type: ignore

    return _validate_timetable_lite(db_timetable, university, specialization)


def _validate_timetable_lite(
        db_timetable: models.Timetable, university: models.University | None,
        specialization: models.Specialization | None) -> TimetableOutLite:
    """Валидирует упрощенное валидное расписание"""
    univ_name = _get_university_name(university)
    spec_name, spec_code, educ_level = _get_specialization_data(specialization)

    return TimetableOutLite(
        id=db_timetable.id, # type: ignore
        name=db_timetable.name, # type: ignore
        university=univ_name, #type: ignore
        specialization_name=spec_name, #type: ignore
        specialization_code=spec_code, #type: ignore
        education_level=educ_level, # type: ignore
        course=db_timetable.course, # type: ignore
        creation_date=db_timetable.creation_date,  # type: ignore
    )


def _validate_public_info_about_user(
        user: models.User | None) -> UserPublicInformation | None:
    """Валидирует публичную информацию пользователя"""
    if not user:
        return None
    return UserPublicInformation(
        id=user.id,  # type: ignore
        email=user.email,  # type: ignore
        first_name=user.first_name,  # type: ignore
        last_name=user.last_name  # type: ignore
    )


def validate_timetable_data_to_search(
        db: Session, data: TimetableSearchRequestForm) -> TimetableSearch:
    """Валидирует и отдает данные для поиска расписания"""
    university_id = _get_university_id(db, data.university)
    specialization_id = _get_specialization_id(db, data.specialization_name, 
        data.specialization_code, data.education_level)

    if data.course:
        _check_course(data.course)

    return TimetableSearch(
        name=data.name,
        course=data.course,
        id_university=university_id,
        id_specialization=specialization_id
    )
