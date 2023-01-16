from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from models import schemas
from controllers.db import get_db
from controllers.user import get_current_user, validate_application, validate_application_for_user
from controllers.timetable import check_user_limit_timetables
from sql import models
from sql.crud import (
    get_timetable_by_id,
    get_timetable_user_status,
    get_timetable_users_relation_by_user_id,
    get_timetable_user_relation_by_user_id_and_timetable_id,
    get_timetables_id_where_user_is_elder,
    create_timetable_user_relation,
    get_application_by_id,
    get_applications_by_timetable_id,
    get_application_by_user_id_and_timetable_id,
    create_application,
    delete_application,
    create_tasks_user_relation_in_timetable
)


router = APIRouter(
    prefix="/application",
    tags=["application"]
)


@router.post(
    path="/submit",
    summary="Submit an application",
    description="Submit an application to be added to the timetable",
)
async def submit_application(
    timetable_id: int,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_user_limit_timetables(user.timetables_info)  # type: ignore

    timetable = get_timetable_by_id(db, timetable_id)
    if not timetable:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unknown timetable"
        )

    user_timetables_id = [timetable.id for timetable in user.timetables_info]  # type: ignore
    if timetable_id in user_timetables_id:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail="The user already has this timetable"
        )

    application = get_application_by_user_id_and_timetable_id(db, user.id, timetable_id)
    if application:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user has already submitted an application to this timetable"
        )

    create_application(db, user.id, timetable_id)


@router.delete("/delete", summary="Delete an application")
async def delete_user_application(
    application_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    user_applications_id = [application.id for application in user.applications]  # type: ignore
    if application_id not in user_applications_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unknown application"
        )
    
    delete_application(db, application_id)


@router.get("/get_all_submitted", summary="Get all user's submitted applications")
async def get_all_submitted_applications(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return {"applications": [validate_application_for_user(db, user.id, application) for application in user.applications]}  # type: ignore


@router.get("/get_all_for_consideration", summary="Get all user's applications for consideration")
async def get_all_applications_for_consideration(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    timetables_id = get_timetables_id_where_user_is_elder(db, user.id)
    if not timetables_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user doesn't have timetables, where he is the elder"
        )

    applications = []
    for timetable_id in timetables_id:
        applications.extend(get_applications_by_timetable_id(db, timetable_id))

    return {"applications": [validate_application(db, application) for application in applications]}  # type: ignore


@router.post("/accept", summary="Add timetable to user")
async def accept_application(
    application_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    application = get_application_by_id(db, application_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unknown application"
        )
    
    user_timetables_id = [timetable.id for timetable in user.timetables_info]  # type: ignore
    if application.id_timetable not in user_timetables_id:  
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user doesn't have this timetable"
        )
    
    timetable_user_status = get_timetable_user_status(db, user.id, application.id_timetable)  # type: ignore
    if timetable_user_status != schemas.TimetableUserStatuses.elder:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"The user doesn't have access rights to add another users to this timetable"
        )

    delete_application(db, application.id)

    user_timetables = get_timetable_users_relation_by_user_id(db, application.id)
    if len(user_timetables) >= 10:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user has too many timetables"
        )

    timetable_user_relation = get_timetable_user_relation_by_user_id_and_timetable_id(db, application.id_user, application.id_timetable)  # type: ignore
    if timetable_user_relation:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail="The user already has this timetable"
        )    

    create_timetable_user_relation(db, application.id_user, application.id_timetable)  # type: ignore
    create_tasks_user_relation_in_timetable(db, application.id_timetable, application.id_user)  # type: ignore


@router.delete("/reject", summary="Reject an application")
async def reject_application(
    application_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    application = get_application_by_id(db, application_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unknown application"
        )
    
    user_timetables_id = [timetable.id for timetable in user.timetables_info]  # type: ignore
    if application.id_timetable not in user_timetables_id:  
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user doesn't have this timetable"
        )
    
    timetable_user_status = get_timetable_user_status(db, user.id, application.id_timetable)  # type: ignore
    if timetable_user_status != schemas.TimetableUserStatuses.elder:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"The user doesn't have access rights to add another users to this timetable"
        )

    delete_application(db, application.id)