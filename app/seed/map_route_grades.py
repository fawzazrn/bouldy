"""Link existing routes to locked grades.

Routes created before grade scales existed only have free-text `grade`. For a
gym that now has a brand, this finds the grade in the brand's scale whose label
matches that text (ignoring case and surrounding spaces) and sets `grade_id`.

It never guesses: text that does not match exactly is only reported, so an
admin can fix those routes by hand.

Usage (dry run by default, nothing is written):

    python -m app.seed.map_route_grades
    python -m app.seed.map_route_grades --apply
"""

import argparse

from sqlalchemy.orm import Session

from app.models.route import Route


def plan_mapping(db: Session):
    """Return (matches, unmatched) for routes at branded gyms with no grade_id."""
    matches = []
    unmatched = []

    routes = (
        db.query(Route)
        .filter(Route.grade_id.is_(None), Route.route_kind.is_(None))
        .all()
    )

    for route in routes:
        brand = route.gym.brand if route.gym else None

        if brand is None:
            continue

        by_label = {
            grade.label.strip().lower(): grade
            for grade in brand.grade_scale.grades
        }
        grade = by_label.get((route.grade or "").strip().lower())

        if grade is None:
            unmatched.append(route)
        else:
            matches.append((route, grade))

    return matches, unmatched


def apply_mapping(db: Session, matches) -> None:
    for route, grade in matches:
        route.grade_id = grade.id
        route.grade = grade.label

    db.commit()


def main() -> None:
    from app.database import SessionLocal

    parser = argparse.ArgumentParser(description="Link existing routes to locked grades.")
    parser.add_argument("--apply", action="store_true", help="write the changes")
    args = parser.parse_args()

    db = SessionLocal()

    try:
        matches, unmatched = plan_mapping(db)

        for route, grade in matches:
            print(f"match     route {route.id} '{route.grade}' -> {grade.label} ({route.gym.name})")

        for route in unmatched:
            print(f"UNMATCHED route {route.id} '{route.grade}' at {route.gym.name}: fix by hand")

        print(f"{len(matches)} matched, {len(unmatched)} unmatched")

        if args.apply:
            apply_mapping(db, matches)
            print("Applied.")
        else:
            print("Dry run. Re-run with --apply to write the matches.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
