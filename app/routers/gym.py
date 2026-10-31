from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import (
    ensure_can_manage_gym,
    get_current_user,
    is_super_admin,
    require_super_admin,
)
from app.models.user import User
from app.crud.gym import (
    create_gym,
    get_gym,
    get_gym_by_name,
    get_gyms,
    update_gym,
    delete_gym,
    GymHasRoutesError,
    BrandNotFoundError,
)
from app.crud.grading import get_gym_grading
from app.schemas.grading import GymGradingResponse
from app.crud.route import get_routes_by_gym
from app.schemas.gym import (
    GymCreate,
    GymUpdate,
    GymResponse,
)
from app.schemas.route import RouteResponse
from app.routers.routes import route_to_response

router = APIRouter(
    prefix="/gyms",
    tags=["Gyms"],
)


@router.post(
    "/",
    response_model=GymResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_gym(
    gym: GymCreate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_super_admin),
):
    if get_gym_by_name(db, gym.name):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Gym name already exists",
        )

    try:
        return create_gym(db, gym)
    except BrandNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Brand not found",
        )


@router.get(
    "/",
    response_model=list[GymResponse],
)
def read_gyms(
    db: Session = Depends(get_db),
):
    return get_gyms(db)


@router.get(
    "/{gym_id}",
    response_model=GymResponse,
)
def read_gym(
    gym_id: int,
    db: Session = Depends(get_db),
):
    gym = get_gym(db, gym_id)

    if gym is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gym not found",
        )

    return gym


@router.get(
    "/{gym_id}/grades",
    response_model=GymGradingResponse,
)
def read_gym_grades(
    gym_id: int,
    db: Session = Depends(get_db),
):
    gym = get_gym(db, gym_id)

    if gym is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gym not found",
        )

    return get_gym_grading(gym)


@router.get(
    "/{gym_id}/routes",
    response_model=list[RouteResponse],
)
def read_gym_routes(
    gym_id: int,
    db: Session = Depends(get_db),
):
    gym = get_gym(db, gym_id)

    if gym is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gym not found",
        )

    routes = get_routes_by_gym(db, gym_id)

    return [
        route_to_response(route)
        for route in routes
    ]


@router.put(
    "/{gym_id}",
    response_model=GymResponse,
)
def update_existing_gym(
    gym_id: int,
    gym_update: GymUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_can_manage_gym(current_user, gym_id)

    # Gym admins edit their gym's details. Identity and brand stay with super admins.
    if not is_super_admin(current_user):
        restricted = {"name", "brand_id", "is_active"} & gym_update.model_fields_set

        if restricted:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Only a super admin can change: {', '.join(sorted(restricted))}",
            )

    try:
        gym = update_gym(
            db=db,
            gym_id=gym_id,
            gym_update=gym_update,
        )
    except BrandNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Brand not found",
        )

    if gym is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gym not found",
        )

    return gym


@router.delete(
    "/{gym_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_gym(
    gym_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_super_admin),
):
    try:
        gym = delete_gym(db, gym_id)
    except GymHasRoutesError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete a gym that still has routes",
        )

    if gym is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gym not found",
        )

    return