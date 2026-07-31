from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.database import get_db
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


@router.post(
    "/",
    response_model=RouteResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_route(
    route: RouteCreate,
    db: Session = Depends(get_db),
):
    db_route = create_route(
        db=db,
        route=route,
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
):
    route = update_route(
        db=db,
        route_id=route_id,
        route_update=route_update,
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
):
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
):
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