from sqlalchemy.orm import Session

from app.models.enums import UserRole
from app.models.gym import Gym
from app.models.user import User, UserGymAdmin


class LastSuperAdminError(Exception):
    """Raised when a change would leave the system with no super admin."""


class GymNotFoundError(Exception):
    pass


class NotGymAdminError(Exception):
    """Gym links can only be given to users whose role is gym_admin."""


def list_users(db: Session, query: str | None = None):
    users = db.query(User).order_by(User.id)

    if query:
        pattern = f"%{query.strip().lower()}%"
        users = users.filter(
            User.email.ilike(pattern) | User.username.ilike(pattern)
        )

    return users.all()


def count_super_admins(db: Session) -> int:
    return (
        db.query(User)
        .filter(User.role == UserRole.SUPER_ADMIN.value)
        .count()
    )


def set_role(db: Session, user: User, role: UserRole) -> User:
    demoting_super = (
        user.role == UserRole.SUPER_ADMIN.value
        and role != UserRole.SUPER_ADMIN
    )

    if demoting_super and count_super_admins(db) <= 1:
        raise LastSuperAdminError(user.id)

    user.role = role.value

    # Gym links only mean something for gym admins.
    if role != UserRole.GYM_ADMIN:
        user.gym_admin_links.clear()

    db.commit()
    db.refresh(user)

    return user


def grant_gym(db: Session, user: User, gym_id: int) -> User:
    if user.role != UserRole.GYM_ADMIN.value:
        raise NotGymAdminError(user.id)

    if db.get(Gym, gym_id) is None:
        raise GymNotFoundError(gym_id)

    if gym_id not in user.admin_gym_ids:
        user.gym_admin_links.append(UserGymAdmin(user_id=user.id, gym_id=gym_id))
        db.commit()
        db.refresh(user)

    return user


def revoke_gym(db: Session, user: User, gym_id: int) -> User:
    for link in list(user.gym_admin_links):
        if link.gym_id == gym_id:
            user.gym_admin_links.remove(link)

    db.commit()
    db.refresh(user)

    return user
