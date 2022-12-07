from fastapi import APIRouter, Depends

from sql import models
from models import schemas
from controllers.user import get_current_user

router = APIRouter()


@router.get("/users/me", response_model=schemas.UserOut, tags=["user"])
async def read_user(user: models.User = Depends(get_current_user)):
    return schemas.UserOut(
        id=user.id, # type: ignore
        email=user.email, # type: ignore 
        first_name=user.first_name, # type: ignore
        last_name=user.last_name # type: ignore
    )
    