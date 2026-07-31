from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate
from app.utils.security import hash_password


def get_user_by_email(
    db: Session,
    email: str,
):
    return (
        db.query(User)
        .filter(User.email == email)
        .first()
    )


def get_user_by_username(
    db: Session,
    username: str,
):
    return (
        db.query(User)
        .filter(User.username == username)
        .first()
    )


def get_user(
    db: Session,
    user_id: int,
):
    return (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )


def create_user(
    db: Session,
    user: UserCreate,
):
    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=hash_password(user.password),
        current_grade=user.current_grade,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user