import jwt
from datetime import datetime, timedelta
from fastapi import Depends

from config import SECRET_KEY, ALGORITHM
from controllers.oauth2 import oauth2_scheme


async def get_token(token: str = Depends(oauth2_scheme)):
    return token


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt