import os


PASSWORD_SALT = os.environ['PASSWORD_SALT']

SECRET_KEY = os.environ['SECRET_KEY']

ALGORITHM = "HS256"

EMAIL = os.environ['EMAIL']

EMAIL_PASSWORD = os.environ['EMAIL_PASSWORD']

ACCESS_TOKEN_EXPIRE_MINUTES = 30

REFRESH_TOKEN_EXPIRE_DAYS = 60

PASS_CHANGE_EXPIRE_MINUTES = 5
