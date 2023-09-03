import jwt
from sqlalchemy.orm import Session
from fastapi import APIRouter, status, Depends, HTTPException

from config import HOST
from models import schemas
from message import (
    USER_NOT_FOUND,
    PASSWORDS_MATCH,
    INCORRECT_EMAIL,
    PASS_CHANGE_REQUEST_CREATED,
    PASS_CHANGE_REQUEST_APPROVED,
    PASS_CHANGE_REQUEST_NOT_FOUND
)
from crud.user import get_user
from crud.pass_change_request import (
    create_password_change_request,
    delete_password_change_request,
    get_password_change_request_by_id,
)
from crud.user import update_user_password
from crud.token import delete_all_user_refresh_token
from controllers.db import get_db
from controllers.token import (
    create_password_change_request_token,
    get_data_from_pass_change_request_token
)
from controllers.mail import send_password_change_email
from controllers.password import get_password_hash, verify_password


router = APIRouter(prefix="/change",tags=["auth"])


@router.patch(
    path="/password/request",
    summary="Создать запрос на изменение пароля пользователя",
    status_code=status.HTTP_200_OK,
    response_description=PASS_CHANGE_REQUEST_CREATED)
async def consider_changing_password(
    pass_change_form_data: schemas.ChangePasswordForm = Depends(),
    db: Session = Depends(get_db)
):
    user = get_user(db, pass_change_form_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=USER_NOT_FOUND)
    
    if verify_password(pass_change_form_data.new_password, user.password):  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=PASSWORDS_MATCH)
    
    new_hash_password = get_password_hash(pass_change_form_data.new_password)
    pass_change_request = create_password_change_request(
        db, pass_change_form_data.email, new_hash_password)
    
    token = create_password_change_request_token(pass_change_request)

    url = f"{HOST}/change/password/execute/{token}"
    send_password_change_email(pass_change_form_data.email, url)


@router.get(
    path="/password/execute/{token}",
    summary="Одобрить запрос на изменение пароля пользователя",
    status_code=status.HTTP_200_OK,
    response_description=PASS_CHANGE_REQUEST_APPROVED)
async def execute_changing_password(token: str, db: Session = Depends(get_db)):

    token_data = get_data_from_pass_change_request_token(token)
    
    pass_change_request = get_password_change_request_by_id(db, token_data.id)
    if not pass_change_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=PASS_CHANGE_REQUEST_NOT_FOUND)

    elif pass_change_request.email != token_data.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=INCORRECT_EMAIL)

    user = get_user(db, token_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=USER_NOT_FOUND)

    update_user_password(db, user.id, pass_change_request.new_password)
    delete_all_user_refresh_token(db, user.id)
    delete_password_change_request(db, pass_change_request.id)
    