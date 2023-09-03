import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, status

from models.schemas import (
    Token,
    AccessToken, 
    RefreshToken,
    PassChangeRequest,
    PassChangeRequestBase
)
from config import (
    ALGORITHM,
    SECRET_KEY,
    REFRESH_TOKEN_EXPIRE_DAYS,
    PASS_CHANGE_EXPIRE_MINUTES,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)


def create_token(data: dict, expires_delta: timedelta | None = None) -> str:
    "Создаёт и возвращает токен"
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def _get_token_expire_stamp(expires_delta: timedelta) -> int:
    "Возвращает POSIX-время, когда срок действия токена истечёт"
    token_time = datetime.utcnow() + expires_delta
    return int(datetime.timestamp(token_time))


def _create_access_token(data: dict, expires_delta: int) -> AccessToken:
    "Создает и возвращает access token и его срок действия"
    access_token_timedelta = timedelta(minutes=expires_delta)
    return AccessToken(
        access_token=create_token(data, access_token_timedelta),
        access_token_expires=_get_token_expire_stamp(access_token_timedelta)
    )


def _create_refresh_token(data: dict, expires_delta: int) -> RefreshToken:
    "Создает и возвращает refresh token и его срок действия"
    refresh_token_timedelta = timedelta(days=expires_delta)
    return RefreshToken(
        refresh_token=create_token(data, refresh_token_timedelta),
        refresh_token_expires=_get_token_expire_stamp(refresh_token_timedelta)
    )

def create_access_and_refresh_tokens(
        data: dict,
        access_expires_delta: int = ACCESS_TOKEN_EXPIRE_MINUTES,
        refresh_expires_delta: int = REFRESH_TOKEN_EXPIRE_DAYS
    ) -> Token:
    "Создает и вовращает access и refresh токены, их сроки действия и тип токенов"
    access_token = _create_access_token(data, access_expires_delta)
    refresh_token = _create_refresh_token(data, refresh_expires_delta)

    return Token(
        access_token=access_token.access_token,
        access_token_expires=access_token.access_token_expires,
        refresh_token=refresh_token.refresh_token,
        refresh_token_expires=refresh_token.refresh_token_expires,
        token_type="bearer"
    )
    

def create_password_change_request_token(request: PassChangeRequest) -> str:
    """Создаёт и возвращает токен для запроса на изменение пароля"""
    data = {"id": request.id, "email": request.email}
    pass_change_expire = timedelta(minutes=PASS_CHANGE_EXPIRE_MINUTES)
    return create_token(data, pass_change_expire)


def get_data_from_pass_change_request_token(token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Could not validate credentials")
        
    try:
        payload = jwt.decode(token, SECRET_KEY, [ALGORITHM])
        request_id = payload.get("id")
        request_email = payload.get("email")
        if not request_id or not request_email:
            raise credentials_exception
        return PassChangeRequestBase(
            id=request_id,
            email=request_email,
        )
    except jwt.PyJWTError:
        raise credentials_exception
