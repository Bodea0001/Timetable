from fastapi import APIRouter, Depends, status, HTTPException

from models.schemas import OAuth2PasswordRequestFormUpdate
from controllers.email import is_email_valid
from controllers.token import get_token
from controllers.user import get_user
from controllers.crud import create_user
from controllers.password import get_password_hash
from sql_app.models import User


router = APIRouter()


@router.post("/register", tags=["register"], status_code=status.HTTP_201_CREATED)
async def process_register(form_data: OAuth2PasswordRequestFormUpdate = Depends()):
    email = form_data.username
    if not is_email_valid(email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid username",
        )
    user = get_user(form_data.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="An account with this email already exists!"
        )
    
    form_data.password = get_password_hash(form_data.password)
    user = User(
        email=form_data.username,
        password=form_data.password,
        first_name=form_data.first_name,
        last_name=form_data.last_name,
    )
    create_user(user)