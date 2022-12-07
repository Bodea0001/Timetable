from sqlalchemy.orm import Session

from sql import models
from models import schemas
from sql.database import SessionLocal, engine

def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.email == username).first()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        email=user.email,
        password=user.password,
        first_name=user.first_name,
        last_name=user.last_name,
        )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user