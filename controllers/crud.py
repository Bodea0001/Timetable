from sqlmodel import Session, select

from sql.models import User, engine, Task


def get_user(username: str):
    with Session(engine) as session:
        statement = select(User).where(User.email == username)
        user: list[User] = session.exec(statement).all()
    if len(user):
        return user[0]


def create_user(user: User):
    with Session(engine) as session:
        session.add(user)
        session.commit()


def create_task(task: Task):
    with Session(engine) as session:
        session.add(task)
        session.commit()
