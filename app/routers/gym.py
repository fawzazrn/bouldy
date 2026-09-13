from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.crud.gym import (
    create_gym,
    get_gym,
    get_gym_by_name,
    get_gyms,
    update_gym,
    delete_gym,
    GymHasRoutesError,
)
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
):
    if get_gym_by_name(db, gym.name):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Gym name already exists",
        )

    return create_gym(db, gym)


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
):
    gym = update_gym(
        db=db,
        gym_id=gym_id,
        gym_update=gym_update,
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