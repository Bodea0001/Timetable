from sqlmodel import SQLModel, Field, create_engine

from config import POSTGRESQL_CONFIG


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(max_length=200, unique=True)
    password: str = Field(max_length=100)
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)


engine = create_engine(POSTGRESQL_CONFIG, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

if __name__=="__main__":
    create_db_and_tables()