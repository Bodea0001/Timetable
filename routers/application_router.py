from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path, status

from sql import models
from controllers.db import get_db
from controllers.user import get_current_user
from controllers.application import accept_application
from controllers.timetable import is_possible_to_add_new_timetable
from crud.timetable_user import (
    exists_timetable_user_relation,
    have_user_enough_rights_in_timetable
)
from crud.timetable import exists_timetable
from crud.application import (
    create_application,
    delete_application,
    have_user_application,
    get_application_by_id,
    exists_application_with_user_id_and_timetable_id
)
from message import (
    TIMETABLE_NOT_FOUND, 
    APPLICATION_NOT_FOUND,
    DUPLICATE_APPLICATION,
    APPLICATION_HAS_BEEN_CREATED,
    APPLICATION_HAS_BEEN_DELETED,
    APPLICATION_HAS_BEEN_ACCEPTED,
    APPLICATION_HAS_BEEN_REJECTED,
    APPLICATION_TO_USER_TIMETABLE,
    USER_DOESNT_HAVE_ENOUGH_RIGHTS,
    TIMETABLE_LIMIT_HAS_BEEN_REACHED,
)


router = APIRouter(tags=["application"])


@router.post(
    path="/timetable/{timetable_id}/submit",
    summary="Подать заявку на добавление к расписанию",
    status_code=status.HTTP_201_CREATED,
    response_description=APPLICATION_HAS_BEEN_CREATED)
async def submit_application(
    timetable_id: int = Path(gt=0),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    if not is_possible_to_add_new_timetable(db, user.id):
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = TIMETABLE_LIMIT_HAS_BEEN_REACHED)

    if not exists_timetable(db, timetable_id):
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = TIMETABLE_NOT_FOUND)

    if exists_timetable_user_relation(db, user.id, timetable_id):
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = APPLICATION_TO_USER_TIMETABLE)

    if exists_application_with_user_id_and_timetable_id(db, user.id, timetable_id):
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = DUPLICATE_APPLICATION)

    create_application(db, user.id, timetable_id)


@router.delete(
    path="/application/{application_id}/delete",
    summary="Удаляет заявку пользователя",
    status_code=status.HTTP_200_OK,
    response_description=APPLICATION_HAS_BEEN_DELETED)
async def delete_user_application(
    application_id: int = Path(gt=0),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    if not have_user_application(db, user.id, application_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=APPLICATION_NOT_FOUND)
    
    delete_application(db, application_id)


@router.post(
    path="/application/{application_id}/accept",
    summary="Одобряет заявку на добавление к расписанию",
    status_code=status.HTTP_200_OK,
    response_description=APPLICATION_HAS_BEEN_ACCEPTED)
async def accept_user_application(
    application_id: int = Path(gt=0),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    application = get_application_by_id(db, application_id)
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=APPLICATION_NOT_FOUND)
    
    if not have_user_enough_rights_in_timetable(
        db, user.id, application.id_timetable):  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=USER_DOESNT_HAVE_ENOUGH_RIGHTS)

    delete_application(db, application.id)

    if not is_possible_to_add_new_timetable(db, application.id_user):  # type: ignore
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = TIMETABLE_LIMIT_HAS_BEEN_REACHED)

    if exists_timetable_user_relation(
        db, application.id_user, application.id_timetable):  # type: ignore
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail=APPLICATION_TO_USER_TIMETABLE)    

    accept_application(db, application)


@router.delete(
    path="/application/{application_id}/reject",
    summary="Отклоняет заявку на добавление к расписанию",
    status_code=status.HTTP_200_OK,
    response_description=APPLICATION_HAS_BEEN_REJECTED)
async def reject_user_application(
    application_id: int = Path(gt=0),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    application = get_application_by_id(db, application_id)

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=APPLICATION_NOT_FOUND)
    
    if not have_user_enough_rights_in_timetable(
        db, user.id, application.id_timetable):  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=USER_DOESNT_HAVE_ENOUGH_RIGHTS)

    delete_application(db, application.id)
