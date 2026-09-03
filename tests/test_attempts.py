"""Tests for attempts: creation rules, ownership scoping, the flash validator."""

from datetime import date

import pytest

from app.models.gym import Gym
from app.models.route import Route
from app.models.session import Session as SessionModel


@pytest.fixture
def gym(db):
    g = Gym(name="Attempt Gym", location="KL")
    db.add(g)
    db.commit()
    db.refresh(g)
    return g


@pytest.fixture
def other_gym(db):
    g = Gym(name="Other Gym", location="JB")
    db.add(g)
    db.commit()
    db.refresh(g)
    return g


@pytest.fixture
def session(db, user, gym):
    s = SessionModel(
        user_id=user.id,
        gym_id=gym.id,
        session_date=date(2026, 2, 1),
        duration_minutes=60,
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


@pytest.fixture
def route(db, gym):
    r = Route(gym_id=gym.id, route_name="Red Arete", grade="V3")
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


def test_create_attempt(auth_client, session, route):
    resp = auth_client.post(
        f"/sessions/{session.id}/attempts",
        json={"route_id": route.id, "num_attempts": 3, "result": "send"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["route_id"] == route.id
    assert body["result"] == "send"
    assert body["num_attempts"] == 3


def test_create_attempt_requires_auth(client, session, route):
    resp = client.post(
        f"/sessions/{session.id}/attempts",
        json={"route_id": route.id, "num_attempts": 1, "result": "flash"},
    )
    assert resp.status_code == 401


def test_attempt_for_route_in_different_gym_is_400(auth_client, db, session, other_gym):
    foreign = Route(gym_id=other_gym.id, route_name="Far Away", grade="V2")
    db.add(foreign)
    db.commit()
    db.refresh(foreign)

    resp = auth_client.post(
        f"/sessions/{session.id}/attempts",
        json={"route_id": foreign.id, "num_attempts": 1, "result": "zone"},
    )
    assert resp.status_code == 400


def test_attempt_for_unknown_route_is_400(auth_client, session):
    resp = auth_client.post(
        f"/sessions/{session.id}/attempts",
        json={"route_id": 9999, "num_attempts": 1, "result": "zone"},
    )
    assert resp.status_code == 400


def test_attempt_for_someone_elses_session_is_400(
    auth_client, db, other_user, route, session
):
    stranger_session = SessionModel(
        user_id=other_user.id,
        gym_id=route.gym_id,
        session_date=date(2026, 2, 2),
        duration_minutes=45,
    )
    db.add(stranger_session)
    db.commit()
    db.refresh(stranger_session)

    resp = auth_client.post(
        f"/sessions/{stranger_session.id}/attempts",
        json={"route_id": route.id, "num_attempts": 1, "result": "send"},
    )
    assert resp.status_code == 400


def test_flash_with_multiple_attempts_is_422(auth_client, session, route):
    resp = auth_client.post(
        f"/sessions/{session.id}/attempts",
        json={"route_id": route.id, "num_attempts": 4, "result": "flash"},
    )
    assert resp.status_code == 422


def test_num_attempts_must_be_at_least_one(auth_client, session, route):
    resp = auth_client.post(
        f"/sessions/{session.id}/attempts",
        json={"route_id": route.id, "num_attempts": 0, "result": "project"},
    )
    assert resp.status_code == 422


def test_list_get_update_delete_attempt(auth_client, session, route):
    created = auth_client.post(
        f"/sessions/{session.id}/attempts",
        json={"route_id": route.id, "num_attempts": 2, "result": "project"},
    ).json()
    attempt_id = created["id"]

    listed = auth_client.get(f"/sessions/{session.id}/attempts")
    assert listed.status_code == 200
    assert [a["id"] for a in listed.json()] == [attempt_id]

    got = auth_client.get(f"/attempts/{attempt_id}")
    assert got.status_code == 200

    patched = auth_client.patch(
        f"/attempts/{attempt_id}",
        json={"result": "send", "num_attempts": 5},
    )
    assert patched.status_code == 200
    assert patched.json()["result"] == "send"
    assert patched.json()["num_attempts"] == 5

    assert auth_client.delete(f"/attempts/{attempt_id}").status_code == 204
    assert auth_client.get(f"/attempts/{attempt_id}").status_code == 404
