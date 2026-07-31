from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session as DBSession

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.session import (
    SessionCreate,
    SessionResponse,
    SessionUpdate,
)
from app.crud.session import (
    create_session,
    delete_session,
    get_session,
    get_sessions_by_user,
    update_session,
)


router = APIRouter(
    prefix="/sessions",
    tags=["Sessions"],
)


@router.post(
    "/",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_session(
    session: SessionCreate,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_session(
        db=db,
        session=session,
        user_id=current_user.id,
    )


@router.get(
    "/",
    response_model=list[SessionResponse],
)
def read_my_sessions(
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_sessions_by_user(
        db=db,
        user_id=current_user.id,
    )


@router.get(
    "/{session_id}",
    response_model=SessionResponse,
)
def read_session(
    session_id: int,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_session = get_session(
        db=db,
        session_id=session_id,
        user_id=current_user.id,
    )

    if db_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    return db_session


@router.put(
    "/{session_id}",
    response_model=SessionResponse,
)
def update_existing_session(
    session_id: int,
    session_update: SessionUpdate,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_session = update_session(
        db=db,
        session_id=session_id,
        user_id=current_user.id,
        session_update=session_update,
    )

    if db_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    return db_session


@router.delete(
    "/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_session(
    session_id: int,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_session = delete_session(
        db=db,
        session_id=session_id,
        user_id=current_user.id,
    )

    if db_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    return