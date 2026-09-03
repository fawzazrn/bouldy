"""Tests for /sessions (auth required, scoped to the current user)."""

from datetime import date

import pytest

from app.models.gym import Gym
from app.models.session import Session as SessionModel


@pytest.fixture
def gym(db):
    g = Gym(name="Session Gym", location="KL")
    db.add(g)
    db.commit()
    db.refresh(g)
    return g


def _session_payload(user_id, gym_id):
    return {
        "user_id": user_id,
        "gym_id": gym_id,
        "session_date": "2026-01-15",
        "duration_minutes": 90,
        "notes": "felt strong",
    }


def test_create_session_requires_auth(client, user, gym):
    resp = client.post("/sessions/", json=_session_payload(user.id, gym.id))
    assert resp.status_code == 401


def test_create_session(auth_client, user, gym):
    resp = auth_client.post("/sessions/", json=_session_payload(user.id, gym.id))
    assert resp.status_code == 201
    body = resp.json()
    assert body["gym_id"] == gym.id
    assert body["duration_minutes"] == 90
    # session is bound to the authenticated user regardless of payload user_id
    assert body["user_id"] == user.id


def test_create_session_ignores_spoofed_user_id(auth_client, user, other_user, gym):
    resp = auth_client.post("/sessions/", json=_session_payload(other_user.id, gym.id))
    assert resp.status_code == 201
    assert resp.json()["user_id"] == user.id


def test_list_only_returns_my_sessions(auth_client, db, user, other_user, gym):
    auth_client.post("/sessions/", json=_session_payload(user.id, gym.id))

    db.add(
        SessionModel(
            user_id=other_user.id,
            gym_id=gym.id,
            session_date=date(2026, 1, 1),
            duration_minutes=30,
        )
    )
    db.commit()

    resp = auth_client.get("/sessions/")
    assert resp.status_code == 200
    rows = resp.json()
    assert len(rows) == 1
    assert rows[0]["user_id"] == user.id


def test_get_session_not_mine_is_404(auth_client, db, other_user, gym):
    theirs = SessionModel(
        user_id=other_user.id,
        gym_id=gym.id,
        session_date=date(2026, 1, 1),
        duration_minutes=30,
    )
    db.add(theirs)
    db.commit()
    db.refresh(theirs)

    assert auth_client.get(f"/sessions/{theirs.id}").status_code == 404


def test_update_session(auth_client, user, gym):
    created = auth_client.post(
        "/sessions/", json=_session_payload(user.id, gym.id)
    ).json()
    resp = auth_client.put(
        f"/sessions/{created['id']}",
        json={"duration_minutes": 120, "notes": "long one"},
    )
    assert resp.status_code == 200
    assert resp.json()["duration_minutes"] == 120


def test_delete_session(auth_client, user, gym):
    created = auth_client.post(
        "/sessions/", json=_session_payload(user.id, gym.id)
    ).json()
    assert auth_client.delete(f"/sessions/{created['id']}").status_code == 204
    assert auth_client.get(f"/sessions/{created['id']}").status_code == 404
