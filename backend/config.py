import os


DATABASE = os.environ['DATABASE']
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_NAME = os.environ['DB_NAME']
DB_HOST = os.environ['DB_HOST']

POSTGRESQL_CONFIG = f"{DATABASE}+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

PASSWORD_SALT = os.environ['PASSWORD_SALT']

SECRET_KEY = os.environ['SECRET_KEY']