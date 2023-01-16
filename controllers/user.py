import jwt
from sqlalchemy import Column, Integer
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status

from sql import models
from sql.crud import get_user, get_user_lite_by_id, get_timetable_by_id
from models import schemas
from models.schemas import TokenData
from controllers.db import get_db
from controllers.oauth2 import oauth2_scheme
from controllers.password import verify_password
from controllers.timetable import get_valid_timetable, get_valid_timetable_lite
from config import SECRET_KEY, ALGORITHM


def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.password):  # type: ignore
        return False
    return user


async def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, [ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.PyJWTError:
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


def get_valid_user(db: Session, user: models.User) -> schemas.UserOut:
    timetables = [get_valid_timetable(db, db_timetable, user.id) for db_timetable in user.timetables_info]  # type: ignore
    applications = [validate_application_for_user(db, user.id, application) for application in user.applications]  # type: ignore
    return schemas.UserOut(
        id=user.id, # type: ignore
        email=user.email, # type: ignore 
        first_name=user.first_name, # type: ignore
        last_name=user.last_name, # type: ignore
        tg_username=user.tg_username,  # type: ignore
        applications=applications,  # type: ignore
        timetables_info=timetables  # type: ignore
    )
    

def validate_application_for_user(
    db: Session, 
    user_id: int | Column[Integer],
    application: models.Application 
) -> schemas.ApplicationOutForUser:
    db_timetable = get_timetable_by_id(db, application.id_timetable)  # type: ignore
    timetable = get_valid_timetable(db, db_timetable, user_id)  # type: ignore
    return schemas.ApplicationOutForUser(
        id=application.id,  # type: ignore
        id_timetable=application.id_timetable,  # type: ignore
        timetable_name=timetable.name,
        timetable_university=timetable.university,
        timetable_specialization_name=timetable.specialization_name,
        timetable_specialization_code=timetable.specialization_code,
        timetable_education_level=timetable.education_level,
        timetable_course=timetable.course,
        creation_date=application.creation_date  #type: ignore
    )


def validate_application(db: Session, application: models.Application) -> schemas.ApplicationOut:
    user_email, user_first_name, user_last_name = get_user_lite_by_id(db, application.id_user)  # type: ignore
    return schemas.ApplicationOut(
        id=application.id,  # type: ignore
        user_email=user_email,  # type: ignore
        user_first_name=user_first_name,  # type: ignore
        user_last_name=user_last_name,  # type: ignore
        id_timetable=application.id_timetable,  # type: ignore
        creation_date=application.creation_date  #type: ignore
    )
