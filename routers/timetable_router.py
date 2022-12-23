from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from models import schemas
from controllers.db import get_db
from controllers.user import get_current_user
from controllers.timetable import (
    check_university,
    get_specialization,
    check_course,
    get_current_timetable,
    validate_timetable,
    check_timetable
    )
from sql import models
from sql.crud import ( 
    get_timetable_by_name_and_user_id,
    create_timetable,
    create_timetable_user,
    get_timetable_by_name_university_id_specialization_id_course,
    get_timetable_user_status,
    update_timetable,
    delete_timetable
    )


router = APIRouter(
    prefix="/timetable",
    tags=["timetable"]
)


@router.post(
    path="/create",
    response_model=schemas.TimetableOutLite,
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
    specialization = get_specialization(db, form_data.specialization_name, form_data.specialization_code, form_data.education_level)
    check_course(form_data.course)
        
    timetable = get_timetable_by_name_and_user_id(db, form_data.name, user.id)
    if timetable:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account already have timetable with this name"
        )
    timetable = get_timetable_by_name_university_id_specialization_id_course(db, \
        form_data.name, university.id, specialization.id, form_data.course)
    if timetable:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Timetable with this data already exists"
        )

    timetable_data = schemas.TimetableCreate(
        name=form_data.name,
        id_university=university.id,  # type: ignore
        id_specialization=specialization.id,  # type: ignore 
        course=form_data.course,
    )
    db_timetable = create_timetable(db, timetable_data)

    timetable_user_relation = schemas.TimetableUser(
        id_user = user.id,  # type: ignore
        id_timetable = db_timetable.id,  # type: ignore
        status = schemas.TimetableUserStatuses.elder
    )
    create_timetable_user(db, timetable_user_relation)

    return validate_timetable(db_timetable, university, specialization)


@router.get(
    path='/get_user_timetable',
    response_model=schemas.TimetableOut,
    summary="Get user's timetable",
    description="Get user's timetable by name, user id", 
    )
async def get_user_timetable(name: str, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return get_current_timetable(db, name, user.id)  # type: ignore


@router.patch(
    path="/update",
    response_model=schemas.TimetableOut,
    summary="Update user's timetable",
    )
async def update_user_timetable(
    timetable_id: int,
    form_data: schemas.TimetableRequestForm = Depends(),
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
    ):
    check_timetable(user, timetable_id)
    
    timetable_user_status = get_timetable_user_status(db, user.id, timetable_id)
    if timetable_user_status != schemas.TimetableUserStatuses.elder:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User doesn't have access rights to change this timetable"
        )
    
    university = check_university(db, form_data.university)
    specialization = get_specialization(db, form_data.specialization_name, form_data.specialization_code, form_data.education_level)
    check_course(form_data.course)
        
    timetable = get_timetable_by_name_and_user_id(db, form_data.name, user.id)
    if timetable:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account already have timetable with this name"
        )
    timetable = get_timetable_by_name_university_id_specialization_id_course(db, \
        form_data.name, university.id, specialization.id, form_data.course)
    if timetable:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Timetable with this data already exists"
        )

    timetable_data = schemas.TimetableCreate(
        name=form_data.name,
        id_university=university.id,  # type: ignore
        id_specialization=specialization.id,  # type: ignore 
        course=form_data.course,
    )
    update_timetable(db, timetable_id, timetable_data)
    return get_current_timetable(db, form_data.name, user.id)


@router.delete("/delete", summary="Delete user's timetable")
async def delete_user_timetable(
    timetable_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
    ):
    check_timetable(user, timetable_id)

    timetable_user_status = get_timetable_user_status(db, user.id, timetable_id)
    if timetable_user_status != schemas.TimetableUserStatuses.elder:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User doesn't have access rights to delete this timetable"
        )    
    delete_timetable(db, timetable_id)


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