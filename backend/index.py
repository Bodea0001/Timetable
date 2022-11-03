import hmac
import json
import base64
import hashlib
from fastapi import FastAPI, Cookie
from sqlmodel import Session, select
from fastapi.responses import Response
from pydantic import EmailStr, BaseModel, Field

from models import User, engine
from config import PASSWORD_SALT, SECRET_KEY


app = FastAPI()


def sign_data(data: str) -> str:
    return hmac.new(
        SECRET_KEY.encode(),
        msg=data.encode(),
        digestmod=hashlib.sha256
    ).hexdigest().upper()


def get_username_from_signed_string(username_signed: str) -> str | None:
    username_base64, sign = username_signed.split(".")
    username = base64.b64decode(username_signed.encode()).decode()
    valid_sign = sign_data(username)
    if hmac.compare_digest(valid_sign, sign):
        return username


@app.get('/')
async def index_page(username: str | None = Cookie(default=None)):
    if not username:
        return Response(
            json.dumps({
                "success": False,
                "message": "You are not logged in!"
            }),
            media_type="aplication/json"
        )

    valid_username = get_username_from_signed_string(username)
    if not valid_username:
        response = Response(
            json.dumps({
                "success": False,
                "message": "Your cookie is not valid!"
            }),
            media_type="aplication/json"
        )
        response.delete_cookie(key="username")
        return response

    with Session(engine) as session:
        statement = select(User).where(User.email == valid_username)
        user = session.exec(statement).all()

    if not user:
        return Response(
            json.dumps({
                "success": False,
                "message": "There is no such user!"
            }),
            media_type="aplication/json"
        )

    return Response(
            json.dumps({
                "success": True,
                "message": "Cookies are correct"
            }),
            media_type="aplication/json"
        )

class RegisterUser(BaseModel):
    email: EmailStr
    password: str = Field(max_length=100)
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)


def get_password_hash(password: str, password_salt: str) -> str:
    full_password = password + password_salt
    password_hash = hashlib.sha256(full_password.encode()).hexdigest().lower()
    return password_hash


def add_user(user: User):
    with Session(engine) as session:
        session.add(user)
        session.commit()


@app.post('/register')
async def process_register_page(data: RegisterUser):
    with Session(engine) as session:
        statement = select(User).where(User.email == data.email)
        user = session.exec(statement).all()

    if user:
        return Response(
            json.dumps({
                "success": False,
                "message": "An account with this email already exists!"
            }),
            media_type="aplication/json"
        )

    data.password = get_password_hash(data.password, PASSWORD_SALT)
    user = User(email=data.email, password=data.password, first_name=data.first_name, last_name=data.last_name)
    add_user(user)

    return Response(
        json.dumps({
            "success": True,
            "message": "Registration completed successfully!"
        }),
        media_type="aplication/json"
    )


class LoginUser(BaseModel):
    email: EmailStr
    password: str = Field(max_length=100)


@app.post('/login')
async def process_login_page(data: LoginUser):
    data.password = get_password_hash(data.password, PASSWORD_SALT)

    with Session(engine) as session:
        statement = select(User).where(User.email == data.email).where(User.password == data.password)
        user = session.exec(statement).all()

    if not user:
        return Response(
            json.dumps({
                "success": False,
                "message": "Incorrect date entered!"
            }),
            media_type="aplication/json"
        )

    response = Response(
            json.dumps({
                "success": True,
                "message": "Verification passed successfully!"
            }),
            media_type="aplication/json"
        )

    username_signed = base64.b64encode(data.email.encode()).decode() + "." + sign_data(data.email)
    response.set_cookie(key="username", value=username_signed)
    print(username_signed)
    return response