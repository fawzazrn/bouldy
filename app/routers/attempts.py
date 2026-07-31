from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.crud.attempt import (
    create_attempt,
    get_attempt,
    get_attempts_by_session,
    update_attempt,
    delete_attempt,
)
from app.schemas.attempt import (
    AttemptCreate,
    AttemptUpdate,
    AttemptResponse,
)
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(
    tags=["Attempts"],
)


# ---------------------------------------------------------
# CREATE ATTEMPT
# POST /sessions/{session_id}/attempts
# ---------------------------------------------------------

@router.post(
    "/sessions/{session_id}/attempts",
    response_model=AttemptResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_attempt(
    session_id: int,
    attempt: AttemptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_attempt = create_attempt(
        db=db,
        session_id=session_id,
        user_id=current_user.id,
        attempt=attempt,
    )

    if db_attempt is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to create attempt. Check session and route.",
        )

    return db_attempt


# ---------------------------------------------------------
# GET ALL ATTEMPTS FOR SESSION
# GET /sessions/{session_id}/attempts
# ---------------------------------------------------------

@router.get(
    "/sessions/{session_id}/attempts",
    response_model=list[AttemptResponse],
)
def read_session_attempts(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    attempts = get_attempts_by_session(
        db=db,
        session_id=session_id,
        user_id=current_user.id,
    )

    return attempts


# ---------------------------------------------------------
# GET ONE ATTEMPT
# GET /attempts/{attempt_id}
# ---------------------------------------------------------

@router.get(
    "/attempts/{attempt_id}",
    response_model=AttemptResponse,
)
def read_attempt(
    attempt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    attempt = get_attempt(
        db=db,
        attempt_id=attempt_id,
        user_id=current_user.id,
    )

    if attempt is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attempt not found",
        )

    return attempt


# ---------------------------------------------------------
# UPDATE ATTEMPT
# PATCH /attempts/{attempt_id}
# ---------------------------------------------------------

@router.patch(
    "/attempts/{attempt_id}",
    response_model=AttemptResponse,
)
def update_existing_attempt(
    attempt_id: int,
    attempt_update: AttemptUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    attempt = update_attempt(
        db=db,
        attempt_id=attempt_id,
        user_id=current_user.id,
        attempt_update=attempt_update,
    )

    if attempt is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attempt not found",
        )

    return attempt


# ---------------------------------------------------------
# DELETE ATTEMPT
# DELETE /attempts/{attempt_id}
# ---------------------------------------------------------

@router.delete(
    "/attempts/{attempt_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_attempt(
    attempt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    attempt = delete_attempt(
        db=db,
        attempt_id=attempt_id,
        user_id=current_user.id,
    )

    if attempt is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attempt not found",
        )

    return None