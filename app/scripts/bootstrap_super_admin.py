"""Make one existing user a super admin.

This is how the first super admin is created, because nobody can promote
themselves through the API. After that, super admins grant roles with
PUT /admin/users/{id}/role.

It shows who the user is and asks for confirmation before changing anything.
Check the name and email carefully: user IDs are different in every database.

Usage:

    python -m app.scripts.bootstrap_super_admin --user-id 1
    python -m app.scripts.bootstrap_super_admin --user-id 1 --yes   # skip the prompt
"""

import argparse

from sqlalchemy.orm import Session

from app.crud.admin import set_role
from app.crud.user import get_user
from app.models.enums import UserRole


class UserNotFound(Exception):
    pass


def promote_to_super_admin(db: Session, user_id: int):
    user = get_user(db, user_id)

    if user is None:
        raise UserNotFound(user_id)

    return set_role(db, user, UserRole.SUPER_ADMIN)


def main() -> None:
    from app.database import SessionLocal

    parser = argparse.ArgumentParser(description="Make a user a super admin.")
    parser.add_argument("--user-id", type=int, required=True)
    parser.add_argument("--yes", action="store_true", help="do not ask for confirmation")
    args = parser.parse_args()

    db = SessionLocal()

    try:
        user = get_user(db, args.user_id)

        if user is None:
            raise SystemExit(f"No user with id {args.user_id}.")

        print(f"User {user.id}: {user.username} <{user.email}> (role: {user.role})")

        if user.role == UserRole.SUPER_ADMIN.value:
            print("Already a super admin. Nothing to do.")
            return

        if not args.yes and input("Make this user a super admin? [y/N] ").strip().lower() != "y":
            raise SystemExit("Cancelled. Nothing was changed.")

        promote_to_super_admin(db, args.user_id)
        print("Done. This user is now a super admin.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
