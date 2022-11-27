from fastapi import APIRouter, Depends

from sql_app.models import User
from controllers.user import get_current_user

router = APIRouter()


@router.get("/users/me", response_model=User, tags=["user"])
async def read_user(user: str = Depends(get_current_user)):
    return user
    