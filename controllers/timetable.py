from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer
from sql import models
from sql.crud import (
    get_university,
    get_specialization_by_name,
    get_specialization_by_code,
    get_timetable_by_name_and_user_id, 
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


def check_education_level(education_level: schemas.Education_level) -> None:
    educ_levels = schemas.Education_level._value2member_map_.keys()
    if education_level not in educ_levels:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid education level"
        )


def get_specialization(
    db: Session,
    specialization_name: str | None,
    specialization_code: str | None,
    education_level: schemas.Education_level,
    ) -> models.Specialization:
    check_education_level(education_level)
    if specialization_name:
        specialization = get_specialization_by_name(db, specialization_name, education_level)
    elif specialization_code:
        specialization = get_specialization_by_code(db, specialization_code, education_level)
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


def check_course(course: int) -> None:
    if not 0 < course < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid course"
        )


def get_current_timetable(db: Session, name: str, user_id: int | Column[Integer]) -> schemas.TimetableOut:
    db_timetable = get_timetable_by_name_and_user_id(db, name, user_id)
    if not db_timetable:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Timetable {name} was not found"
        )
    return get_valid_timetable(db, db_timetable)


def get_valid_timetable(db: Session, db_timetable: models.Timetable) -> schemas.TimetableOut:
    university = get_university_by_id(db, db_timetable.id_university)  # type: ignore
    if not university:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The university was not found, change the university from the timetable"
        )
    
    specialization = get_specialization_by_id(db, db_timetable.id_specialization) #type: ignore
    if not specialization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The specialization was not found, change the specialization from the timetable"
        )

    return validate_timetable(db_timetable, university, specialization)
  

def validate_timetable(
    db_timetable: models.Timetable,
    university: models.University,
    specialization: models.Specialization
    ) -> schemas.TimetableOut:
    return schemas.TimetableOut(
        id=db_timetable.id, # type: ignore
        name=db_timetable.name, # type: ignore
        university=university.name, #type: ignore
        specialization_name=specialization.name, #type: ignore
        specialization_code=specialization.code, #type: ignore
        education_level=specialization.education_level, # type: ignore
        course=db_timetable.course, # type: ignore
        upper_week_items=db_timetable.upper_week_items, # type: ignore
        lower_week_items=db_timetable.lower_week_items, # type: ignore
        tasks=db_timetable.tasks, # type: ignore
    )