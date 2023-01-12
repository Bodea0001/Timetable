import jwt
from datetime import timedelta
from sqlalchemy.orm import Session
from fastapi import APIRouter, status, Depends, HTTPException

from sql.crud import (
    get_user,
    create_password_change_request,
    get_password_change_request_by_id,
    delete_password_change_request,
    update_user_password,
    delete_all_user_refresh_token,
)
from models import schemas
from controllers.db import get_db
from controllers.token import create_token
from controllers.mail import send_password_change_email
from controllers.password import get_password_hash, verify_password
from config import PASS_CHANGE_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM


router = APIRouter(
    prefix="/change",
    tags=["auth"]
)


@router.patch(
    path="/password/request",
    status_code=status.HTTP_200_OK,
    summary="Request the user's password change"
)
async def consider_changing_password(
    pass_change_form_data: schemas.ChangePasswordForm = Depends(),
    db: Session = Depends(get_db)
):
    user = get_user(db, pass_change_form_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unknown user"
        )
    
    if verify_password(pass_change_form_data.new_password, user.password):  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The user uses this password"
        )
    
    new_hash_password = get_password_hash(pass_change_form_data.new_password)
    pass_change_request = create_password_change_request(db, pass_change_form_data.email, new_hash_password)
    
    data = {"id": pass_change_request.id, "email": pass_change_request.email}
    pass_change_expire = timedelta(minutes=PASS_CHANGE_EXPIRE_MINUTES)
    token = create_token(data, pass_change_expire)
    url = f"http://localhost:8000/change_password/execute/{token}"
    send_password_change_email(pass_change_form_data.email, url)


@router.get(
    path="/password/execute/{token}",
    status_code=status.HTTP_200_OK,
    summary="Change the user's password"
)
async def execute_changing_password(token: str, db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, [ALGORITHM])
        request_id = payload.get("id")
        request_email = payload.get("email")
        if not request_id or not request_email:
            raise credentials_exception
        token_data = schemas.PassChangeRequestBase(
            id=request_id,
            email=request_email,
        )
    except jwt.PyJWTError:
        raise credentials_exception
    
    pass_change_request = get_password_change_request_by_id(db, token_data.id)
    if not pass_change_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unknown request"
        )
    elif pass_change_request.email != token_data.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect user's email"
        )

    user = get_user(db, token_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unknown user"
        )

    update_user_password(db, user.id, pass_change_request.new_password)
    delete_all_user_refresh_token(db, user.id)
    delete_password_change_request(db, pass_change_request.id)
    