"""Tests for /gyms CRUD, acting as a super admin (see test_permissions.py for roles)."""

import pytest


@pytest.fixture
def gym(admin_client):
    resp = admin_client.post(
        "/gyms/",
        json={"name": "Boulder Central", "location": "Kuala Lumpur"},
    )
    assert resp.status_code == 201
    return resp.json()


def test_create_gym(gym):
    assert gym["id"] > 0
    assert gym["name"] == "Boulder Central"
    assert gym["location"] == "Kuala Lumpur"


def test_list_gyms_includes_created(admin_client, gym):
    resp = admin_client.get("/gyms/")
    assert resp.status_code == 200
    ids = [g["id"] for g in resp.json()]
    assert gym["id"] in ids


def test_get_gym_by_id(admin_client, gym):
    resp = admin_client.get(f"/gyms/{gym['id']}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Boulder Central"


def test_get_missing_gym_is_404(admin_client):
    resp = admin_client.get("/gyms/9999")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Gym not found"


def test_update_gym(admin_client, gym):
    resp = admin_client.put(f"/gyms/{gym['id']}", json={"location": "Penang"})
    assert resp.status_code == 200
    assert resp.json()["location"] == "Penang"
    assert resp.json()["name"] == "Boulder Central"  # untouched


def test_update_missing_gym_is_404(admin_client):
    resp = admin_client.put("/gyms/9999", json={"name": "Nope"})
    assert resp.status_code == 404


def test_delete_gym(admin_client, gym):
    assert admin_client.delete(f"/gyms/{gym['id']}").status_code == 204
    assert admin_client.get(f"/gyms/{gym['id']}").status_code == 404


def test_delete_missing_gym_is_404(admin_client):
    assert admin_client.delete("/gyms/9999").status_code == 404


def test_create_gym_duplicate_name_is_409(admin_client, gym):
    resp = admin_client.post(
        "/gyms/",
        json={"name": gym["name"], "location": "Somewhere else"},
    )
    assert resp.status_code == 409


def test_delete_gym_with_routes_is_409(admin_client, gym):
    resp = admin_client.post(
        "/routes/",
        json={
            "gym_id": gym["id"],
            "route_name": "Blue Traverse",
            "grade": "V5",
            "styles": [],
        },
    )
    assert resp.status_code == 201

    resp = admin_client.delete(f"/gyms/{gym['id']}")
    assert resp.status_code == 409
    assert admin_client.get(f"/gyms/{gym['id']}").status_code == 200


def test_get_gym_routes(admin_client, gym):
    other = admin_client.post(
        "/gyms/", json={"name": "Other Gym", "location": "Elsewhere"}
    ).json()
    mine = admin_client.post(
        "/routes/",
        json={
            "gym_id": gym["id"],
            "route_name": "Mine",
            "grade": "V3",
            "styles": [],
        },
    ).json()
    admin_client.post(
        "/routes/",
        json={
            "gym_id": other["id"],
            "route_name": "Not Mine",
            "grade": "V3",
            "styles": [],
        },
    )

    resp = admin_client.get(f"/gyms/{gym['id']}/routes")
    assert resp.status_code == 200
    ids = [r["id"] for r in resp.json()]
    assert ids == [mine["id"]]


def test_get_routes_for_missing_gym_is_404(admin_client):
    assert admin_client.get("/gyms/9999/routes").status_code == 404


def test_get_gym_routes_empty_when_none_created(admin_client, gym):
    resp = admin_client.get(f"/gyms/{gym['id']}/routes")
    assert resp.status_code == 200
    assert resp.json() == []
