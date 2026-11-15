from sqlalchemy.orm import Session, selectinload

from app.models.enums import ROUTE_KIND_GRADE_TEXT, RouteKind
from app.models.grading import Grade, GradeScale, GymBrand
from app.models.gym import Gym


class GradeValidationError(Exception):
    """A route's grade or kind is not allowed for its gym."""


def get_brands(db: Session):
    return db.query(GymBrand).order_by(GymBrand.name).all()


def get_brand(db: Session, brand_id: int):
    return (
        db.query(GymBrand)
        .options(
            selectinload(GymBrand.grade_scale).selectinload(GradeScale.grades)
        )
        .filter(GymBrand.id == brand_id)
        .first()
    )


def get_grade(db: Session, grade_id: int):
    return db.query(Grade).filter(Grade.id == grade_id).first()


def resolve_route_grade(
    db: Session,
    gym: Gym,
    grade_text: str | None,
    grade_id: int | None,
    route_kind: RouteKind | str | None,
):
    """Check grade and kind against the gym's brand.

    Returns (grade_text, grade_id, route_kind) ready to store. The text is the
    value for the legacy routes.grade column, so older clients keep working.
    """
    brand = gym.brand
    kind = RouteKind(route_kind) if route_kind else None

    if kind is not None:
        if brand is None or kind.value not in brand.allowed_route_kinds:
            raise GradeValidationError(
                f"Route kind '{kind.value}' is not available at this gym"
            )

    if grade_id is not None:
        if brand is None:
            raise GradeValidationError("This gym has no grade scale")

        grade = get_grade(db, grade_id)

        if grade is None or grade.scale_id != brand.grade_scale_id:
            raise GradeValidationError(
                "Grade does not belong to this gym's grade scale"
            )

        return grade.label, grade.id, kind.value if kind else None

    # No locked grade supplied.
    if brand is not None:
        if kind is None:
            raise GradeValidationError(
                "grade_id is required for gyms with a grade scale"
            )
        return ROUTE_KIND_GRADE_TEXT[kind], None, kind.value

    # Gym without a brand: original free-text behaviour.
    if not grade_text or not grade_text.strip():
        raise GradeValidationError("grade is required")

    return grade_text.strip(), None, None


def get_gym_grading(gym: Gym):
    brand = gym.brand

    return {
        "gym_id": gym.id,
        "brand_id": brand.id if brand else None,
        "scale": brand.grade_scale if brand else None,
        "allowed_route_kinds": brand.allowed_route_kinds if brand else [],
        "grade_required": brand is not None,
    }
