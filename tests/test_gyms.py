"""Tests for /gyms CRUD (no auth required by the current router)."""

import pytest


@pytest.fixture
def gym(client):
    resp = client.post(
        "/gyms/",
        json={"name": "Boulder Central", "location": "Kuala Lumpur"},
    )
    assert resp.status_code == 201
    return resp.json()


def test_create_gym(gym):
    assert gym["id"] > 0
    assert gym["name"] == "Boulder Central"
    assert gym["location"] == "Kuala Lumpur"


def test_list_gyms_includes_created(client, gym):
    resp = client.get("/gyms/")
    assert resp.status_code == 200
    ids = [g["id"] for g in resp.json()]
    assert gym["id"] in ids


def test_get_gym_by_id(client, gym):
    resp = client.get(f"/gyms/{gym['id']}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Boulder Central"


def test_get_missing_gym_is_404(client):
    resp = client.get("/gyms/9999")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Gym not found"


def test_update_gym(client, gym):
    resp = client.put(f"/gyms/{gym['id']}", json={"location": "Penang"})
    assert resp.status_code == 200
    assert resp.json()["location"] == "Penang"
    assert resp.json()["name"] == "Boulder Central"  # untouched


def test_update_missing_gym_is_404(client):
    resp = client.put("/gyms/9999", json={"name": "Nope"})
    assert resp.status_code == 404


def test_delete_gym(client, gym):
    assert client.delete(f"/gyms/{gym['id']}").status_code == 204
    assert client.get(f"/gyms/{gym['id']}").status_code == 404


def test_delete_missing_gym_is_404(client):
    assert client.delete("/gyms/9999").status_code == 404


def test_create_gym_duplicate_name_is_409(client, gym):
    resp = client.post(
        "/gyms/",
        json={"name": gym["name"], "location": "Somewhere else"},
    )
    assert resp.status_code == 409


def test_delete_gym_with_routes_is_409(client, gym):
    resp = client.post(
        "/routes/",
        json={
            "gym_id": gym["id"],
            "route_name": "Blue Traverse",
            "grade": "V5",
            "styles": [],
        },
    )
    assert resp.status_code == 201

    resp = client.delete(f"/gyms/{gym['id']}")
    assert resp.status_code == 409
    assert client.get(f"/gyms/{gym['id']}").status_code == 200


def test_get_gym_routes(client, gym):
    other = client.post(
        "/gyms/", json={"name": "Other Gym", "location": "Elsewhere"}
    ).json()
    mine = client.post(
        "/routes/",
        json={
            "gym_id": gym["id"],
            "route_name": "Mine",
            "grade": "V3",
            "styles": [],
        },
    ).json()
    client.post(
        "/routes/",
        json={
            "gym_id": other["id"],
            "route_name": "Not Mine",
            "grade": "V3",
            "styles": [],
        },
    )

    resp = client.get(f"/gyms/{gym['id']}/routes")
    assert resp.status_code == 200
    ids = [r["id"] for r in resp.json()]
    assert ids == [mine["id"]]


def test_get_routes_for_missing_gym_is_404(client):
    assert client.get("/gyms/9999/routes").status_code == 404


def test_get_gym_routes_empty_when_none_created(client, gym):
    resp = client.get(f"/gyms/{gym['id']}/routes")
    assert resp.status_code == 200
    assert resp.json() == []
