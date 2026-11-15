from sqlalchemy.orm import Session
from datetime import date

from app.models.gym import Gym
from app.models.route import Route
from app.models.route_style_association import RouteStyleAssociation
from app.schemas.route import RouteCreate, RouteUpdate
from app.models.enums import RouteStatus
from app.crud.grading import GradeValidationError, resolve_route_grade


def create_route(
    db: Session,
    route: RouteCreate,
):
    gym = db.query(Gym).filter(Gym.id == route.gym_id).first()

    if gym is None:
        return None

    grade_text, grade_id, route_kind = resolve_route_grade(
        db,
        gym,
        route.grade,
        route.grade_id,
        route.route_kind,
    )

    route_data = route.model_dump(
        exclude={"styles", "grade", "grade_id", "route_kind"}
    )

    db_route = Route(
        **route_data,
        grade=grade_text,
        grade_id=grade_id,
        route_kind=route_kind,
    )

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

    grade_fields = {"gym_id", "grade", "grade_id", "route_kind"}

    if grade_fields & update_data.keys():
        gym = db.query(Gym).filter(
            Gym.id == update_data.get("gym_id", db_route.gym_id)
        ).first()

        if gym is None:
            raise GradeValidationError("Gym not found")

        # Sending only free-text `grade` means the old grade_id no longer applies.
        if "grade" in update_data and "grade_id" not in update_data:
            effective_grade_id = None
        else:
            effective_grade_id = update_data.get("grade_id", db_route.grade_id)

        grade_text, grade_id, route_kind = resolve_route_grade(
            db,
            gym,
            update_data.get("grade", db_route.grade),
            effective_grade_id,
            update_data.get("route_kind", db_route.route_kind),
        )

        update_data["grade"] = grade_text
        update_data["grade_id"] = grade_id
        update_data["route_kind"] = route_kind

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