from sqlalchemy.orm import Session as DBSession

from app.models.session import Session
from app.schemas.session import SessionCreate, SessionUpdate


def create_session(
    db: DBSession,
    session: SessionCreate,
    user_id: int,
):
    db_session = Session(
        **session.model_dump(),
        user_id=user_id,
    )

    db.add(db_session)
    db.commit()
    db.refresh(db_session)

    return db_session


def get_sessions_by_user(
    db: DBSession,
    user_id: int,
):
    return (
        db.query(Session)
        .filter(Session.user_id == user_id)
        .order_by(Session.session_date.desc())
        .all()
    )


def get_session(
    db: DBSession,
    session_id: int,
    user_id: int,
):
    return (
        db.query(Session)
        .filter(
            Session.id == session_id,
            Session.user_id == user_id,
        )
        .first()
    )


def update_session(
    db: DBSession,
    session_id: int,
    user_id: int,
    session_update: SessionUpdate,
):
    db_session = get_session(
        db,
        session_id,
        user_id,
    )

    if db_session is None:
        return None

    update_data = session_update.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(db_session, key, value)

    db.commit()
    db.refresh(db_session)

    return db_session


def delete_session(
    db: DBSession,
    session_id: int,
    user_id: int,
):
    db_session = get_session(
        db,
        session_id,
        user_id,
    )

    if db_session is None:
        return None

    db.delete(db_session)
    db.commit()

    return db_session