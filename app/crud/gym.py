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


def delete_gym(db: Session, gym_id: int):
    gym = get_gym(db, gym_id)

    if gym is None:
        return None

    db.delete(gym)
    db.commit()

    return gym