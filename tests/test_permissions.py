"""Permission matrix for gym and route writes, and role management.

These tests use real bearer tokens (no dependency override), so they exercise
the whole auth layer. Roles under test:

- anonymous: no token
- plain user
- gym admin of gym A (not gym B)
- super admin
"""

import pytest

from app.models.gym import Gym
from app.models.route import Route
from tests.conftest import auth_headers, make_user


@pytest.fixture
def gym_a(db):
    g = Gym(name="Gym A", location="KL")
    db.add(g)
    db.commit()
    return g


@pytest.fixture
def gym_b(db):
    g = Gym(name="Gym B", location="JB")
    db.add(g)
    db.commit()
    return g


@pytest.fixture
def route_a(db, gym_a):
    r = Route(gym_id=gym_a.id, route_name="A1", grade="V3")
    db.add(r)
    db.commit()
    return r


@pytest.fixture
def route_b(db, gym_b):
    r = Route(gym_id=gym_b.id, route_name="B1", grade="V3")
    db.add(r)
    db.commit()
    return r


@pytest.fixture
def plain(db):
    return make_user(db, "plain")


@pytest.fixture
def admin_a(db, gym_a):
    return make_user(db, "admin_a", role="gym_admin", gym_ids=[gym_a.id])


@pytest.fixture
def boss(db):
    return make_user(db, "boss", role="super_admin")


def route_body(gym):
    return {"gym_id": gym.id, "route_name": "New", "grade": "V1"}


# --- reads stay public -----------------------------------------------------


def test_reads_need_no_login(client, gym_a, route_a):
    assert client.get("/gyms/").status_code == 200
    assert client.get(f"/gyms/{gym_a.id}").status_code == 200
    assert client.get(f"/gyms/{gym_a.id}/routes").status_code == 200
    assert client.get("/routes/").status_code == 200
    assert client.get(f"/routes/{route_a.id}").status_code == 200
    assert client.get("/brands/").status_code == 200


# --- anonymous -------------------------------------------------------------


def test_anonymous_cannot_write_anything(client, gym_a, route_a):
    assert client.post("/gyms/", json={"name": "X", "location": "Y"}).status_code == 401
    assert client.put(f"/gyms/{gym_a.id}", json={"phone": "1"}).status_code == 401
    assert client.delete(f"/gyms/{gym_a.id}").status_code == 401
    assert client.post("/routes/", json=route_body(gym_a)).status_code == 401
    assert client.put(f"/routes/{route_a.id}", json={"wall": "w"}).status_code == 401
    assert client.delete(f"/routes/{route_a.id}").status_code == 401
    assert client.patch(f"/routes/{route_a.id}/retire").status_code == 401
    assert client.get("/admin/users").status_code == 401


# --- plain user ------------------------------------------------------------


def test_plain_user_cannot_write_gyms_or_routes(client, plain, gym_a, route_a):
    h = auth_headers(plain)

    assert client.post("/gyms/", json={"name": "X", "location": "Y"}, headers=h).status_code == 403
    assert client.put(f"/gyms/{gym_a.id}", json={"phone": "1"}, headers=h).status_code == 403
    assert client.delete(f"/gyms/{gym_a.id}", headers=h).status_code == 403
    assert client.post("/routes/", json=route_body(gym_a), headers=h).status_code == 403
    assert client.put(f"/routes/{route_a.id}", json={"wall": "w"}, headers=h).status_code == 403
    assert client.delete(f"/routes/{route_a.id}", headers=h).status_code == 403
    assert client.patch(f"/routes/{route_a.id}/retire", headers=h).status_code == 403


def test_plain_user_cannot_use_admin_endpoints(client, plain):
    assert client.get("/admin/users", headers=auth_headers(plain)).status_code == 403


# --- gym admin -------------------------------------------------------------


def test_gym_admin_manages_routes_of_their_own_gym(client, admin_a, gym_a, route_a):
    h = auth_headers(admin_a)

    created = client.post("/routes/", json=route_body(gym_a), headers=h)
    assert created.status_code == 201

    assert client.put(f"/routes/{route_a.id}", json={"wall": "Cave"}, headers=h).status_code == 200
    assert client.patch(f"/routes/{route_a.id}/retire", headers=h).status_code == 200
    assert client.delete(f"/routes/{created.json()['id']}", headers=h).status_code == 204


def test_gym_admin_cannot_touch_another_gyms_routes(client, admin_a, gym_b, route_b):
    h = auth_headers(admin_a)

    assert client.post("/routes/", json=route_body(gym_b), headers=h).status_code == 403
    assert client.put(f"/routes/{route_b.id}", json={"wall": "w"}, headers=h).status_code == 403
    assert client.delete(f"/routes/{route_b.id}", headers=h).status_code == 403
    assert client.patch(f"/routes/{route_b.id}/retire", headers=h).status_code == 403


def test_gym_admin_cannot_move_a_route_into_another_gym(client, admin_a, route_a, gym_b):
    resp = client.put(
        f"/routes/{route_a.id}",
        json={"gym_id": gym_b.id, "grade": "V1"},
        headers=auth_headers(admin_a),
    )

    assert resp.status_code == 403


def test_gym_admin_edits_details_of_their_own_gym(client, admin_a, gym_a):
    resp = client.put(
        f"/gyms/{gym_a.id}",
        json={"address": "New address", "opening_hours": "10am to 10pm", "phone": "012"},
        headers=auth_headers(admin_a),
    )

    assert resp.status_code == 200
    assert resp.json()["address"] == "New address"


def test_gym_admin_cannot_edit_another_gym(client, admin_a, gym_b):
    resp = client.put(
        f"/gyms/{gym_b.id}", json={"phone": "1"}, headers=auth_headers(admin_a)
    )

    assert resp.status_code == 403


@pytest.mark.parametrize(
    "body", [{"name": "Renamed"}, {"brand_id": 1}, {"is_active": False}]
)
def test_gym_admin_cannot_change_identity_fields(client, admin_a, gym_a, body):
    resp = client.put(f"/gyms/{gym_a.id}", json=body, headers=auth_headers(admin_a))

    assert resp.status_code == 403


def test_gym_admin_cannot_create_or_delete_gyms(client, admin_a, gym_a):
    h = auth_headers(admin_a)

    assert client.post("/gyms/", json={"name": "X", "location": "Y"}, headers=h).status_code == 403
    assert client.delete(f"/gyms/{gym_a.id}", headers=h).status_code == 403


def test_gym_admin_role_without_links_manages_nothing(client, db, gym_a):
    orphan = make_user(db, "orphan", role="gym_admin")

    resp = client.post("/routes/", json=route_body(gym_a), headers=auth_headers(orphan))

    assert resp.status_code == 403


# --- super admin -----------------------------------------------------------


def test_super_admin_can_manage_every_gym_and_route(client, boss, gym_a, route_b):
    h = auth_headers(boss)

    created = client.post("/gyms/", json={"name": "New Gym", "location": "Penang"}, headers=h)
    assert created.status_code == 201
    new_id = created.json()["id"]

    assert client.put(f"/gyms/{new_id}", json={"name": "Renamed"}, headers=h).status_code == 200
    assert client.post("/routes/", json=route_body(gym_a), headers=h).status_code == 201
    assert client.put(f"/routes/{route_b.id}", json={"wall": "w"}, headers=h).status_code == 200
    assert client.delete(f"/gyms/{new_id}", headers=h).status_code == 204


def test_missing_route_is_404_for_admins(client, boss):
    assert client.put("/routes/999", json={"wall": "w"}, headers=auth_headers(boss)).status_code == 404
    assert client.delete("/routes/999", headers=auth_headers(boss)).status_code == 404


# --- /auth/me --------------------------------------------------------------


def test_me_reports_role_and_admin_gyms(client, admin_a, gym_a):
    body = client.get("/auth/me", headers=auth_headers(admin_a)).json()

    assert body["role"] == "gym_admin"
    assert body["admin_gym_ids"] == [gym_a.id]


def test_me_for_plain_user(client, plain):
    body = client.get("/auth/me", headers=auth_headers(plain)).json()

    assert body["role"] == "user"
    assert body["admin_gym_ids"] == []


def test_register_always_creates_a_plain_user(client):
    resp = client.post(
        "/auth/register",
        json={
            "username": "sneaky",
            "email": "sneaky@example.com",
            "password": "pw12345678",
            "role": "super_admin",
        },
    )
    assert resp.status_code == 201

    token = client.post(
        "/auth/login",
        data={"username": "sneaky@example.com", "password": "pw12345678"},
    ).json()["access_token"]
    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"}).json()

    assert me["role"] == "user"


# --- role management -------------------------------------------------------


def test_super_admin_grants_gym_admin_for_specific_gyms(client, boss, plain, gym_a, gym_b):
    h = auth_headers(boss)

    assert client.put(f"/admin/users/{plain.id}/role", json={"role": "gym_admin"}, headers=h).status_code == 200
    assert client.put(f"/admin/users/{plain.id}/gyms/{gym_a.id}", headers=h).status_code == 200
    resp = client.put(f"/admin/users/{plain.id}/gyms/{gym_b.id}", headers=h)

    assert sorted(resp.json()["admin_gym_ids"]) == sorted([gym_a.id, gym_b.id])
    # The new rights apply straight away.
    assert client.post("/routes/", json=route_body(gym_b), headers=auth_headers(plain)).status_code == 201


def test_granting_a_gym_requires_the_gym_admin_role_first(client, boss, plain, gym_a):
    resp = client.put(f"/admin/users/{plain.id}/gyms/{gym_a.id}", headers=auth_headers(boss))

    assert resp.status_code == 409


def test_granting_an_unknown_gym_is_404(client, boss, admin_a):
    resp = client.put(f"/admin/users/{admin_a.id}/gyms/999", headers=auth_headers(boss))

    assert resp.status_code == 404


def test_revoking_a_gym_removes_the_rights(client, boss, admin_a, gym_a):
    resp = client.delete(f"/admin/users/{admin_a.id}/gyms/{gym_a.id}", headers=auth_headers(boss))

    assert resp.status_code == 200
    assert resp.json()["admin_gym_ids"] == []
    assert client.post("/routes/", json=route_body(gym_a), headers=auth_headers(admin_a)).status_code == 403


def test_demoting_a_gym_admin_clears_their_gyms(client, boss, admin_a):
    resp = client.put(f"/admin/users/{admin_a.id}/role", json={"role": "user"}, headers=auth_headers(boss))

    assert resp.json()["role"] == "user"
    assert resp.json()["admin_gym_ids"] == []


def test_unknown_role_is_422(client, boss, plain):
    resp = client.put(f"/admin/users/{plain.id}/role", json={"role": "emperor"}, headers=auth_headers(boss))

    assert resp.status_code == 422


def test_cannot_demote_the_last_super_admin(client, boss):
    resp = client.put(f"/admin/users/{boss.id}/role", json={"role": "user"}, headers=auth_headers(boss))

    assert resp.status_code == 409


def test_can_demote_a_super_admin_when_another_exists(client, db, boss):
    other = make_user(db, "boss2", role="super_admin")

    resp = client.put(f"/admin/users/{other.id}/role", json={"role": "user"}, headers=auth_headers(boss))

    assert resp.status_code == 200


def test_gym_admin_cannot_grant_roles(client, admin_a, plain):
    resp = client.put(f"/admin/users/{plain.id}/role", json={"role": "super_admin"}, headers=auth_headers(admin_a))

    assert resp.status_code == 403


def test_user_cannot_promote_themselves(client, plain):
    resp = client.put(f"/admin/users/{plain.id}/role", json={"role": "super_admin"}, headers=auth_headers(plain))

    assert resp.status_code == 403


def test_user_search(client, boss, plain, admin_a):
    resp = client.get("/admin/users?q=ADMIN_A", headers=auth_headers(boss))

    assert [u["username"] for u in resp.json()] == ["admin_a"]


def test_role_change_for_missing_user_is_404(client, boss):
    resp = client.put("/admin/users/999/role", json={"role": "user"}, headers=auth_headers(boss))

    assert resp.status_code == 404


# --- bootstrap script ------------------------------------------------------


def test_bootstrap_promotes_the_given_user(db, plain):
    from app.scripts.bootstrap_super_admin import promote_to_super_admin

    promoted = promote_to_super_admin(db, plain.id)

    assert promoted.role == "super_admin"


def test_bootstrap_unknown_user(db):
    from app.scripts.bootstrap_super_admin import UserNotFound, promote_to_super_admin

    with pytest.raises(UserNotFound):
        promote_to_super_admin(db, 999)
