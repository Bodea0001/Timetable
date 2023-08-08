from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError

from routers import (
    login,
    register,
    user_info,
    task_router,
    week_router,
    logout_router,
    refresh_router,
    timetable_router,
    application_router,
    credentials_change_router,
)


app = FastAPI()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder({"detail": exc.errors()})
    )


app.include_router(login.router)
app.include_router(register.router)
app.include_router(user_info.router)
app.include_router(task_router.router)
app.include_router(week_router.router)
app.include_router(logout_router.router)
app.include_router(refresh_router.router)
app.include_router(timetable_router.router)
app.include_router(application_router.router)
app.include_router(credentials_change_router.router)
