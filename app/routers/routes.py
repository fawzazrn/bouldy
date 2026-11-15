from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import ensure_can_manage_gym, get_current_user
from app.models.user import User
from app.crud.grading import GradeValidationError
from app.crud.route import (
    create_route,
    delete_route,
    get_route,
    get_routes,
    get_routes_by_gym,
    update_route,
    retire_route,
)
from app.schemas.route import (
    RouteCreate,
    RouteResponse,
    RouteUpdate,
)


router = APIRouter(
    prefix="/routes",
    tags=["Routes"],
)


def route_to_response(route):
    return {
        "id": route.id,
        "gym_id": route.gym_id,
        "route_name": route.route_name,
        "grade": route.grade,
        "grade_id": route.grade_id,
        "route_kind": route.route_kind,
        "colour": route.colour,
        "wall": route.wall,
        "setter": route.setter,
        "set_date": route.set_date,
        "retired_date": route.retired_date,
        "status": route.status,
        "styles": [
            item.style
            for item in route.styles
        ],
    }


def _get_route_or_404(db: Session, route_id: int):
    route = get_route(db=db, route_id=route_id)

    if route is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Route not found",
        )

    return route


@router.post(
    "/",
    response_model=RouteResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_route(
    route: RouteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_can_manage_gym(current_user, route.gym_id)

    try:
        db_route = create_route(
            db=db,
            route=route,
        )
    except GradeValidationError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        )

    if db_route is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Gym not found",
        )

    return route_to_response(db_route)


@router.get(
    "/",
    response_model=list[RouteResponse],
)
def read_routes(
    db: Session = Depends(get_db),
):
    routes = get_routes(db)

    return [
        route_to_response(route)
        for route in routes
    ]


@router.get(
    "/{route_id}",
    response_model=RouteResponse,
)
def read_route(
    route_id: int,
    db: Session = Depends(get_db),
):
    route = get_route(
        db=db,
        route_id=route_id,
    )

    if route is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Route not found",
        )

    return route_to_response(route)


@router.put(
    "/{route_id}",
    response_model=RouteResponse,
)
def update_existing_route(
    route_id: int,
    route_update: RouteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = _get_route_or_404(db, route_id)

    ensure_can_manage_gym(current_user, existing.gym_id)

    # Moving a route to another gym needs rights over both.
    if route_update.gym_id is not None:
        ensure_can_manage_gym(current_user, route_update.gym_id)

    try:
        route = update_route(
            db=db,
            route_id=route_id,
            route_update=route_update,
        )
    except GradeValidationError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        )

    if route is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Route not found",
        )

    return route_to_response(route)


@router.delete(
    "/{route_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_route(
    route_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_can_manage_gym(
        current_user,
        _get_route_or_404(db, route_id).gym_id,
    )

    route = delete_route(
        db=db,
        route_id=route_id,
    )

    if route is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Route not found",
        )

    return

@router.patch(
    "/{route_id}/retire",
    response_model=RouteResponse,
)
def retire_existing_route(
    route_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_can_manage_gym(
        current_user,
        _get_route_or_404(db, route_id).gym_id,
    )

    route = retire_route(
        db=db,
        route_id=route_id,
    )

    if route is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Route not found",
        )

    return route_to_response(route)