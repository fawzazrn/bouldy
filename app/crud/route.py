from sqlalchemy.orm import Session
from datetime import date

from app.models.route import Route
from app.models.route_style_association import RouteStyleAssociation
from app.schemas.route import RouteCreate, RouteUpdate
from app.models.enums import RouteStatus


def create_route(
    db: Session,
    route: RouteCreate,
):
    route_data = route.model_dump(
        exclude={"styles"}
    )

    db_route = Route(**route_data)

    db_route.styles = [
        RouteStyleAssociation(style=style)
        for style in route.styles
    ]

    db.add(db_route)
    db.commit()
    db.refresh(db_route)

    return db_route


def get_routes(db: Session):
    return (
        db.query(Route)
        .order_by(Route.id.desc())
        .all()
    )


def get_route(
    db: Session,
    route_id: int,
):
    return (
        db.query(Route)
        .filter(Route.id == route_id)
        .first()
    )


def get_routes_by_gym(
    db: Session,
    gym_id: int,
):
    return (
        db.query(Route)
        .filter(Route.gym_id == gym_id)
        .order_by(Route.id.desc())
        .all()
    )


def update_route(
    db: Session,
    route_id: int,
    route_update: RouteUpdate,
):
    db_route = get_route(
        db=db,
        route_id=route_id,
    )

    if db_route is None:
        return None

    update_data = route_update.model_dump(
        exclude_unset=True,
        exclude={"styles"},
    )

    for key, value in update_data.items():
        setattr(db_route, key, value)

    if route_update.styles is not None:
        db_route.styles.clear()

        db_route.styles.extend(
            RouteStyleAssociation(style=style)
            for style in route_update.styles
        )

    db.commit()
    db.refresh(db_route)

    return db_route


def delete_route(
    db: Session,
    route_id: int,
):
    db_route = get_route(
        db=db,
        route_id=route_id,
    )

    if db_route is None:
        return None

    db.delete(db_route)
    db.commit()

    return db_route

def retire_route(
    db: Session,
    route_id: int,
):
    route = get_route(
        db=db,
        route_id=route_id,
    )

    if route is None:
        return None

    route.status = RouteStatus.RETIRED
    route.retired_date = date.today()

    db.commit()
    db.refresh(route)

    return route