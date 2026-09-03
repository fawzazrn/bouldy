"""Shared test fixtures.

Every test runs against a throwaway in-memory SQLite database, never Neon.
The `get_db` dependency is swapped for one bound to that database, and
`get_current_user` can be swapped for a fixed user so protected endpoints
can be tested without juggling real JWTs.
"""

import os

# These must be set BEFORE `app.*` is imported: app/database.py builds an engine
# at import time, and app/utils/security.py raises if JWT_SECRET_KEY is missing.
# setdefault means a real .env still wins for everything except the DB URL here.
os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-not-for-production-0123456789")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "60")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.dependencies.auth import get_current_user
from app.main import app
from app.models.user import User
from app.utils.security import create_access_token, hash_password

# One shared connection for the whole process (StaticPool) so the in-memory DB
# survives across sessions/threads within a test.
engine = create_engine(
    "sqlite+pysqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


@event.listens_for(engine, "connect")
def _enable_sqlite_fks(dbapi_connection, _):
    """SQLite ignores FK constraints unless asked."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


@pytest.fixture
def db():
    """A fresh schema + session per test; dropped afterwards for isolation."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db):
    """TestClient whose request handlers use the test database."""

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def user(db):
    """A persisted user, password is 'password123'."""
    u = User(
        username="climber",
        email="climber@example.com",
        password_hash=hash_password("password123"),
        current_grade="V4",
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


@pytest.fixture
def other_user(db):
    """A second persisted user, for 'not mine' / ownership tests."""
    u = User(
        username="stranger",
        email="stranger@example.com",
        password_hash=hash_password("password123"),
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


@pytest.fixture
def auth_client(client, user):
    """TestClient where `get_current_user` always resolves to `user`."""
    app.dependency_overrides[get_current_user] = lambda: user
    yield client
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture
def token(user):
    """A real signed JWT for `user` (use when testing the auth layer itself)."""
    return create_access_token(user.id)
