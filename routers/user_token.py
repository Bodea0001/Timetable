from fastapi import APIRouter, Depends

from controllers.token import get_token

router = APIRouter()


@router.get('/token', tags=["token"])
async def read_token(token: str = Depends(get_token)):
    return token