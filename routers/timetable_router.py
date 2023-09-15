from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path

from sql import models
from models import schemas
from crud.timetable_user import (
    exists_timetable_user_relation,
    delete_timetable_user_relation,
    have_user_enough_rights_in_timetable,
    exists_another_user_timetables_with_name
)
from crud.timetable import (
    get_timetables,
    delete_timetable,
    exists_timetable_with_timetable_data,
    exists_timetable_with_user_id_and_name, 
)
from controllers.db import get_db
from controllers.user import get_current_user
from controllers.timetable import (
    update_timetable,
    get_valid_timetable,
    get_valid_timetables,
    get_valid_timetable_lite,
    get_valid_timetables_lite,
    create_timetable_for_user,
    is_possible_to_add_new_timetable,
    validate_timetable_data_to_search,
    validate_timetable_data_to_create_or_update,
)
from message import (
    ELDER_CANT_LEAVE,
    LEAVING_TIMETABLE,
    DELETING_TIMETABLE,
    DUPLICATE_TIMETABLE,
    ARGUMENTS_NOT_PASSED,
    SEARCH_YIELDED_NO_RESULTS,
    USER_DOESNT_HAVE_TIMETABLE,
    DUPLICATE_OF_TIMETABLE_NAME,
    USER_DOESNT_HAVE_ENOUGH_RIGHTS, 
    TIMETABLE_LIMIT_HAS_BEEN_REACHED,
)


router = APIRouter(prefix="/timetable", tags=["timetable"])


@router.get(
    path='/my',
    summary="Возвращает расписания пользователя",
    response_model=list[schemas.TimetableOut],
    status_code=status.HTTP_200_OK)
async def get_user_timetable(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    return get_valid_timetables(db, user.timetables_info, user.id)  # type: ignore


@router.get(
    path='/my/lite',
    summary="Возвращает расписания пользователя в упрощенном виде",
    response_model=list[schemas.TimetableOutLite],
    status_code=status.HTTP_200_OK)
async def get_user_timetable_lite(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    return get_valid_timetables_lite(db, user.timetables_info)  # type: ignore


@router.get(
    path="/find",
    summary="Находит расписания по данным",
    response_model=list[schemas.TimetableOutLite],
    status_code=status.HTTP_200_OK)
async def find_timetables(
    search_data: schemas.TimetableSearchRequestForm = Depends(),
    skip: int = Query(default=0, ge=0),
    size: int = Query(default=10, gt=0, le=10),
    db: Session = Depends(get_db)
):
    if not search_data.have_any_arguments():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ARGUMENTS_NOT_PASSED)

    valid_search_data = validate_timetable_data_to_search(db, search_data)

    timetables = get_timetables(db, valid_search_data, skip, size)  
    if not timetables:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=SEARCH_YIELDED_NO_RESULTS)

    return get_valid_timetables_lite(db, timetables)


@router.post(
    path="/create",
    summary="Создаёт новое расписание",
    response_model=schemas.TimetableOut,
    status_code=status.HTTP_201_CREATED)
async def create_new_timetable(
    form_data: schemas.TimetableRequestForm = Depends(),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    if not is_possible_to_add_new_timetable(db, user.id):
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = TIMETABLE_LIMIT_HAS_BEEN_REACHED)

    if exists_timetable_with_user_id_and_name(db, form_data.name, user.id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=DUPLICATE_OF_TIMETABLE_NAME)

    timetable_data = validate_timetable_data_to_create_or_update(db, form_data)
        
    if exists_timetable_with_timetable_data(db, timetable_data):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=DUPLICATE_TIMETABLE)

    timetable = create_timetable_for_user(db, timetable_data, user.id)

    return get_valid_timetable(db, timetable, user.id)


@router.patch(
    path="/{timetable_id}/update",
    summary="Обновляет данные расписания",
    response_model=schemas.TimetableOut,
    status_code=status.HTTP_200_OK)
async def update_user_timetable(
    timetable_id: int = Path(gt=0),
    form_data: schemas.TimetableRequestForm = Depends(),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):    
    if not have_user_enough_rights_in_timetable(db, user.id, timetable_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=USER_DOESNT_HAVE_ENOUGH_RIGHTS)
    
    if exists_another_user_timetables_with_name(
        db, form_data.name, user.id, timetable_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=DUPLICATE_OF_TIMETABLE_NAME)

    timetable_data = validate_timetable_data_to_create_or_update(db, form_data)
        
    if exists_timetable_with_timetable_data(db, timetable_data):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=DUPLICATE_TIMETABLE)

    timetable = update_timetable(db, timetable_id, timetable_data)

    return get_valid_timetable(db, timetable, user.id)


@router.delete(
    path="/{timetable_id}/delete",
    summary="Удаляет расписание для всех",
    status_code=status.HTTP_200_OK,
    response_description=DELETING_TIMETABLE)
async def delete_timetable_for_all(
    timetable_id: int = Path(gt=0),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    if not have_user_enough_rights_in_timetable(db, user.id, timetable_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=USER_DOESNT_HAVE_ENOUGH_RIGHTS)
        
    delete_timetable(db, timetable_id)


@router.delete(
    path="/{timetable_id}/leave",
    summary="Удаляет расписание у пользователя",
    status_code=status.HTTP_200_OK,
    response_description=LEAVING_TIMETABLE)
async def delete_timetable_for_user(
    timetable_id: int = Path(gt=0),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    if not exists_timetable_user_relation(db, user.id, timetable_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=USER_DOESNT_HAVE_TIMETABLE)

    if not have_user_enough_rights_in_timetable(
        db, user.id, timetable_id, [schemas.TimetableUserStatuses.user]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,  
            detail=ELDER_CANT_LEAVE) 
    
    delete_timetable_user_relation(db, user.id, timetable_id)
