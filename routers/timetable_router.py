from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from models import schemas
from controllers.db import get_db
from controllers.user import get_current_user
from controllers.checking import (
    check_university,
    check_specialization,
    check_education_level,
    check_course,
    check_user_timetable_status,
    get_current_timetable,
    get_valid_timetable,
    )
from sql import models
from sql.crud import ( 
    get_timetable, 
    create_timetable,
    get_timetables_by_user_id,
    )


router = APIRouter(
    prefix="/timetable",
    tags=["timetable"]
)


@router.post(
    path="/create",
    response_model=schemas.TimetableOut,
    summary="Create a new timetable",
    description="Create a new timetable by name, university, specialization, education level, course, user id, status", 
    status_code=status.HTTP_201_CREATED,
    )
async def create_new_timetable(
    form_data: schemas.TimetableRequestForm = Depends(),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
    ):
    university = check_university(db, form_data.university)
    specialization = check_specialization(db, form_data.specialization_name, form_data.specialization_code)
    check_education_level(form_data.education_level)
    check_course(form_data.course)
    form_data.status = check_user_timetable_status(form_data.status)

    timetable = get_timetable(db, user.id, form_data.name)
    if timetable:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account already have timetable with this name"
        )

    timetable_data = schemas.TimetableCreate(
        name=form_data.name,
        id_university=university.id, # type: ignore
        id_specialization=specialization.id, # type: ignore
        education_level=form_data.education_level,
        course=form_data.course,
        id_user=user.id, # type: ignore
        status=form_data.status
    )
    db_timetable = create_timetable(db, timetable_data)
    return schemas.TimetableOut(
        id=db_timetable.id, # type: ignore
        name=db_timetable.name, # type: ignore
        university=form_data.university,
        specialization_name=form_data.specialization_name,
        specialization_code=form_data.specialization_code,
        education_level=db_timetable.education_level, # type: ignore
        course=db_timetable.course, # type: ignore
        id_user=db_timetable.id_user, # type: ignore
        status=db_timetable.status, # type: ignore
        upper_week_items=db_timetable.upper_week_items, # type: ignore
        lower_week_items=db_timetable.lower_week_items, # type: ignore
        tasks=db_timetable.tasks, # type: ignore
    )


@router.get(
    path='/get_user_timetable',
    response_model=schemas.TimetableOut,
    summary="Get user's timetable",
    description="Get user's timetable by name, user id", 
    )
async def get_user_timetable(name: str, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return get_current_timetable(db, name, user.id)  # type: ignore


@router.get(
    path="/get_user_timetables",
    response_model=list[schemas.TimetableOutLite],
    summary="Get all user's timetables",
    description="Get all user's timetables by user id", 
)
async def get_user_timetables(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    db_timetables = get_timetables_by_user_id(db, user.id) # type: ignore
    if not db_timetables:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User don't have timetables",
        )
    print('\n', db_timetables, '\n')
    timetables = []
    for db_timetable in db_timetables:
        timetable = get_valid_timetable(db, db_timetable)
        timetables.append(timetable)
    return timetables


# @router.get(
#     path="/get_timetables",
#     response_model=list[schemas.TimetableOutLite],
#     summary="Get timetables",
#     description="Get timetables by name, university, specialization, course",
# )
# async def get_timetables(
#     name: str | None = None,
#     university_name: str | None = None,
#     specialization_name: str | None = None,
#     specialization_code: str | None = None,
#     course: int | None = None,
#     db: Session = Depends(get_db)
#     ):
#     if not any([name, university_name, specialization_name, specialization_code, course]):
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Arguments not passed"
#         )

#     if not name:
#         name = models.Timetable.name
        
#     if university_name:
#         university = get_university(db, university_name)
#         university_id = university.id
#     else:
#         university_id = models.Timetable.id_university

#     if specialization_name:
#         specialization = get_specialization_by_name(db, specialization_name)
#         specialization_id = specialization.id
#     elif specialization_code:
#         specialization = get_specialization_by_code(db, specialization_code)
#         specialization_id = specialization.id
#     else:
#         specialization_id = models.Timetable.id_speсialization

#     if not course:
#         course = models.Timetable.course  # type: ignore
#     else:
#         check_course(course)

#     db_timetables = filter_timetablse(db, name, university_id, specialization_id, course)    # type: ignore
#     if not db_timetables:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Timetables not found"
#         )
#     timetables = []
#     for db_timetable in db_timetables:
#         timetable = get_valid_timetable(db, db_timetable)
#         timetables.append(timetable)
#     return timetables    