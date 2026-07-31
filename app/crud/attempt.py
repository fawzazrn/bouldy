from sqlalchemy.orm import Session as DBSession

from app.models.attempt import Attempt
from app.models.route import Route
from app.models.session import Session
from app.schemas.attempt import AttemptCreate, AttemptUpdate


def create_attempt(
    db: DBSession,
    session_id: int,
    user_id: int,
    attempt: AttemptCreate,
):
    # Check session exists and belongs to current user
    db_session = (
        db.query(Session)
        .filter(
            Session.id == session_id,
            Session.user_id == user_id,
        )
        .first()
    )

    if db_session is None:
        return None

    # Check route exists
    route = (
        db.query(Route)
        .filter(Route.id == attempt.route_id)
        .first()
    )

    if route is None:
        return None

    # Route must belong to the same gym as session
    if route.gym_id != db_session.gym_id:
        return None

    db_attempt = Attempt(
        session_id=session_id,
        route_id=attempt.route_id,
        num_attempts=attempt.num_attempts,
        result=attempt.result,
        notes=attempt.notes,
    )

    db.add(db_attempt)
    db.commit()
    db.refresh(db_attempt)

    return db_attempt


def get_attempt(
    db: DBSession,
    attempt_id: int,
    user_id: int,
):
    return (
        db.query(Attempt)
        .join(
            Session,
            Attempt.session_id == Session.id,
        )
        .filter(
            Attempt.id == attempt_id,
            Session.user_id == user_id,
        )
        .first()
    )


def get_attempts_by_session(
    db: DBSession,
    session_id: int,
    user_id: int,
):
    return (
        db.query(Attempt)
        .join(
            Session,
            Attempt.session_id == Session.id,
        )
        .filter(
            Attempt.session_id == session_id,
            Session.user_id == user_id,
        )
        .order_by(Attempt.id)
        .all()
    )


def update_attempt(
    db: DBSession,
    attempt_id: int,
    user_id: int,
    attempt_update: AttemptUpdate,
):
    db_attempt = get_attempt(
        db=db,
        attempt_id=attempt_id,
        user_id=user_id,
    )

    if db_attempt is None:
        return None

    update_data = attempt_update.model_dump(
        exclude_unset=True,
    )

    for key, value in update_data.items():
        setattr(db_attempt, key, value)

    db.commit()
    db.refresh(db_attempt)

    return db_attempt


def delete_attempt(
    db: DBSession,
    attempt_id: int,
    user_id: int,
):
    db_attempt = get_attempt(
        db=db,
        attempt_id=attempt_id,
        user_id=user_id,
    )

    if db_attempt is None:
        return None

    db.delete(db_attempt)
    db.commit()

    return db_attempt