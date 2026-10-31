import os

import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.crud.user import get_user
from app.models.enums import UserRole


SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={
            "WWW-Authenticate": "Bearer"
        },
    )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        user_id = int(user_id)

    except (InvalidTokenError, ValueError):
        raise credentials_exception

    user = get_user(
        db=db,
        user_id=user_id,
    )

    if user is None:
        raise credentials_exception

    return user


def is_super_admin(user) -> bool:
    return user.role == UserRole.SUPER_ADMIN.value


def can_manage_gym(user, gym_id: int) -> bool:
    """Super admins manage every gym. Gym admins only the gyms linked to them."""
    if is_super_admin(user):
        return True

    return (
        user.role == UserRole.GYM_ADMIN.value
        and gym_id in user.admin_gym_ids
    )


def require_super_admin(user=Depends(get_current_user)):
    if not is_super_admin(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required",
        )

    return user


def ensure_can_manage_gym(user, gym_id: int) -> None:
    """Raise 403 unless the user may edit this gym and its routes."""
    if not can_manage_gym(user, gym_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not an admin of this gym",
        )