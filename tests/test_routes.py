"""Tests for /routes CRUD, styles, and the retire action."""

import pytest

from app.models.gym import Gym


@pytest.fixture
def gym(db):
    g = Gym(name="Route Gym", location="KL")
    db.add(g)
    db.commit()
    db.refresh(g)
    return g


@pytest.fixture
def route(client, gym):
    resp = client.post(
        "/routes/",
        json={
            "gym_id": gym.id,
            "route_name": "Blue Traverse",
            "grade": "V5",
            "colour": "blue",
            "wall": "cave",
            "styles": ["Crimps", "Slopers"],
        },
    )
    assert resp.status_code == 201
    return resp.json()


def test_create_route_defaults_to_active(route):
    assert route["status"] == "active"
    assert route["retired_date"] is None
    assert sorted(route["styles"]) == ["Crimps", "Slopers"]


def test_get_route(client, route):
    resp = client.get(f"/routes/{route['id']}")
    assert resp.status_code == 200
    assert resp.json()["route_name"] == "Blue Traverse"


def test_get_missing_route_is_404(client):
    assert client.get("/routes/4242").status_code == 404


def test_list_routes(client, route):
    resp = client.get("/routes/")
    assert resp.status_code == 200
    assert any(r["id"] == route["id"] for r in resp.json())


def test_update_route_grade_and_styles(client, route):
    resp = client.put(
        f"/routes/{route['id']}",
        json={"grade": "V6", "styles": ["Pinches"]},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["grade"] == "V6"
    assert body["styles"] == ["Pinches"]


def test_retire_route_sets_status_and_date(client, route):
    resp = client.patch(f"/routes/{route['id']}/retire")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "retired"
    assert body["retired_date"] is not None


def test_delete_route(client, route):
    assert client.delete(f"/routes/{route['id']}").status_code == 204
    assert client.get(f"/routes/{route['id']}").status_code == 404


def test_create_route_rejects_unknown_style(client, gym):
    resp = client.post(
        "/routes/",
        json={
            "gym_id": gym.id,
            "route_name": "Bad Style",
            "grade": "V1",
            "styles": ["NotARealStyle"],
        },
    )
    assert resp.status_code == 422
