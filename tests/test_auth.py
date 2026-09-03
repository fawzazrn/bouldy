"""Tests for /auth: register, login, token handling, /auth/me."""


def test_register_creates_user(client):
    resp = client.post(
        "/auth/register",
        json={
            "username": "newbie",
            "email": "newbie@example.com",
            "password": "hunter2hunter",
            "current_grade": "V2",
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == "newbie@example.com"
    assert body["username"] == "newbie"
    assert "id" in body
    # the hash must never be serialised back to the client
    assert "password" not in body
    assert "password_hash" not in body


def test_register_rejects_duplicate_email(client):
    payload = {
        "username": "a",
        "email": "dupe@example.com",
        "password": "pw12345678",
    }
    assert client.post("/auth/register", json=payload).status_code == 201

    payload["username"] = "b"
    resp = client.post("/auth/register", json=payload)
    assert resp.status_code == 409
    assert resp.json()["detail"] == "Email already registered"


def test_register_rejects_duplicate_username(client):
    assert client.post(
        "/auth/register",
        json={"username": "same", "email": "one@example.com", "password": "pw12345678"},
    ).status_code == 201

    resp = client.post(
        "/auth/register",
        json={"username": "same", "email": "two@example.com", "password": "pw12345678"},
    )
    assert resp.status_code == 409
    assert resp.json()["detail"] == "Username already taken"


def test_register_rejects_invalid_email(client):
    resp = client.post(
        "/auth/register",
        json={"username": "x", "email": "not-an-email", "password": "pw12345678"},
    )
    assert resp.status_code == 422


def test_login_returns_bearer_token(client, user):
    resp = client.post(
        "/auth/login",
        data={"username": "climber@example.com", "password": "password123"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_wrong_password_is_401(client, user):
    resp = client.post(
        "/auth/login",
        data={"username": "climber@example.com", "password": "wrong"},
    )
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Incorrect email or password"


def test_login_unknown_email_is_401(client):
    resp = client.post(
        "/auth/login",
        data={"username": "ghost@example.com", "password": "whatever"},
    )
    assert resp.status_code == 401


def test_me_with_valid_token(client, token):
    resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == "climber@example.com"


def test_me_without_token_is_401(client):
    assert client.get("/auth/me").status_code == 401


def test_me_with_garbage_token_is_401(client):
    resp = client.get("/auth/me", headers={"Authorization": "Bearer not.a.jwt"})
    assert resp.status_code == 401


def test_register_then_login_roundtrip(client):
    client.post(
        "/auth/register",
        json={"username": "round", "email": "round@example.com", "password": "pw12345678"},
    )
    login = client.post(
        "/auth/login",
        data={"username": "round@example.com", "password": "pw12345678"},
    )
    token = login.json()["access_token"]
    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["username"] == "round"
