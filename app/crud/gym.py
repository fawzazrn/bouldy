from sqlalchemy.orm import Session

from app.models.gym import Gym
from app.schemas.gym import GymCreate, GymUpdate


def create_gym(db: Session, gym: GymCreate) -> Gym:
    db_gym = Gym(**gym.model_dump())

    db.add(db_gym)
    db.commit()
    db.refresh(db_gym)

    return db_gym


def get_gyms(db: Session):
    return db.query(Gym).all()


def get_gym(db: Session, gym_id: int):
    return db.query(Gym).filter(Gym.id == gym_id).first()


def get_gym_by_name(db: Session, name: str):
    return db.query(Gym).filter(Gym.name == name).first()


def update_gym(
    db: Session,
    gym_id: int,
    gym_update: GymUpdate,
):
    gym = get_gym(db, gym_id)

    if gym is None:
        return None

    update_data = gym_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(gym, key, value)

    db.commit()
    db.refresh(gym)

    return gym


class GymHasRoutesError(Exception):
    """Raised when deleting a gym that still has routes referencing it."""


def delete_gym(db: Session, gym_id: int):
    gym = get_gym(db, gym_id)

    if gym is None:
        return None

    if gym.routes:
        raise GymHasRoutesError(gym_id)

    db.delete(gym)
    db.commit()

    return gym