from fastapi import FastAPI

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
