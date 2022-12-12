from fastapi import FastAPI

from routers import login, register, user_info, user_token, task_router, timetable_router


app = FastAPI()


app.include_router(login.router)
app.include_router(register.router)
app.include_router(user_info.router)
app.include_router(user_token.router)
app.include_router(task_router.router)
app.include_router(timetable_router.router)
