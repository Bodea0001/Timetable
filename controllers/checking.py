from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from sql import models
from sql.crud import (
    get_university,
    get_specialization_by_name,
    get_specialization_by_code,
    get_timetable, 
    get_university_by_id, 
    get_specialization_by_id
    )
from models import schemas


def check_university(db: Session, university_name: str) -> models.University:
    university = get_university(db, university_name)
    if not university:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid university",
        )
    return university


def check_specialization(
    db: Session,
    specialization_name: str | None = None,
    specialization_code: str | None = None
    ) -> models.Specialization:
    if specialization_name:
        specialization = get_specialization_by_name(db, specialization_name)
    elif specialization_code:
        specialization = get_specialization_by_code(db, specialization_code)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Specialization has not been introduced"
        )
    if not specialization:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid specialization",
        )
    return specialization


def check_education_level(education_level: schemas.Education_level) -> None:
    educ_levels = schemas.Education_level._value2member_map_.keys()
    if education_level not in educ_levels:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid education level"
        )


def check_course(course: int) -> None:
    if not 0 < course < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid course"
        )


def check_user_timetable_status(status: schemas.TimetableStatuses | None) -> schemas.TimetableStatuses:
    if not status:
        return schemas.TimetableStatuses.elder
    return status


def get_current_timetable(db: Session, name: str, user_id: int) -> schemas.TimetableOut:
    db_timetable = get_timetable(db, user_id, name) # type: ignore
    if not db_timetable:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Timetable {name} was not found"
        )
    return get_valid_timetable(db, db_timetable)

    

def get_valid_timetable(db: Session, db_timetable: models.Timetable) -> schemas.TimetableOut:
    university = get_university_by_id(db, db_timetable.id_university) # type: ignore
    if not university:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The university was not found, change the university from the timetable"
        )
    
    specialization = get_specialization_by_id(db, db_timetable.id_speсialization) #type: ignore
    if not specialization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The specialization was not found, change the specialization from the timetable"
        )

    return schemas.TimetableOut(
        id=db_timetable.id, # type: ignore
        name=db_timetable.name, # type: ignore
        university=university.name, #type: ignore
        specialization_name=specialization.name, #type: ignore
        specialization_code=specialization.code, #type: ignore
        education_level=db_timetable.education_level, # type: ignore
        course=db_timetable.course, # type: ignore
        id_user=db_timetable.id_user, # type: ignore
        status=db_timetable.status, # type: ignore
        upper_week_items=db_timetable.upper_week_items, # type: ignore
        lower_week_items=db_timetable.lower_week_items, # type: ignore
        tasks=db_timetable.tasks, # type: ignore
    )