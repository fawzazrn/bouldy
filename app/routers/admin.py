"""Granting and revoking admin roles. Super admins only."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.admin import (
    GymNotFoundError,
    LastSuperAdminError,
    NotGymAdminError,
    grant_gym,
    list_users,
    revoke_gym,
    set_role,
)
from app.crud.user import get_user
from app.database import get_db
from app.dependencies.auth import require_super_admin
from app.schemas.user import AdminUserResponse, RoleUpdate

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(require_super_admin)],
)


def _get_user_or_404(db: Session, user_id: int):
    user = get_user(db, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


@router.get(
    "/users",
    response_model=list[AdminUserResponse],
)
def read_users(
    q: str | None = None,
    db: Session = Depends(get_db),
):
    """List users, optionally filtered by part of the email or username."""
    return list_users(db, q)


@router.put(
    "/users/{user_id}/role",
    response_model=AdminUserResponse,
)
def update_user_role(
    user_id: int,
    body: RoleUpdate,
    db: Session = Depends(get_db),
):
    user = _get_user_or_404(db, user_id)

    try:
        return set_role(db, user, body.role)
    except LastSuperAdminError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot remove the last super admin",
        )


@router.put(
    "/users/{user_id}/gyms/{gym_id}",
    response_model=AdminUserResponse,
)
def add_gym_admin(
    user_id: int,
    gym_id: int,
    db: Session = Depends(get_db),
):
    user = _get_user_or_404(db, user_id)

    try:
        return grant_gym(db, user, gym_id)
    except NotGymAdminError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Set the user's role to gym_admin first",
        )
    except GymNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gym not found",
        )


@router.delete(
    "/users/{user_id}/gyms/{gym_id}",
    response_model=AdminUserResponse,
)
def remove_gym_admin(
    user_id: int,
    gym_id: int,
    db: Session = Depends(get_db),
):
    user = _get_user_or_404(db, user_id)

    return revoke_gym(db, user, gym_id)
