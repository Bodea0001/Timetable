from fastapi import FastAPI

from routers import login, register, user_info, user_token


app = FastAPI()


app.include_router(login.router)
app.include_router(register.router)
app.include_router(user_info.router)
app.include_router(user_token.router)