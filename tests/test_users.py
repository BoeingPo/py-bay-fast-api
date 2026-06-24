def register(client, email, password="password123"):
    return client.post(
        "/users/register",
        json={"email": email, "name": "Test User", "password": password},
    )


def login(client, email, password="password123"):
    return client.post("/users/login", data={"username": email, "password": password})


def test_register_creates_user(client, unique_email):
    res = register(client, unique_email)
    assert res.status_code == 201
    body = res.json()
    assert body["email"] == unique_email
    assert body["name"] == "Test User"
    assert "id" in body


def test_register_duplicate_email_rejected(client, unique_email):
    register(client, unique_email)
    res = register(client, unique_email)
    assert res.status_code == 409


def test_login_sets_cookie_and_returns_user(client, unique_email):
    register(client, unique_email)
    res = login(client, unique_email)
    assert res.status_code == 200
    assert res.json()["email"] == unique_email
    assert "access_token" in res.cookies


def test_login_wrong_password_rejected(client, unique_email):
    register(client, unique_email)
    res = login(client, unique_email, password="wrong-password")
    assert res.status_code == 401


def test_me_requires_authentication(client):
    res = client.get("/users/me")
    assert res.status_code == 401


def test_me_returns_current_user_after_login(client, unique_email):
    register(client, unique_email)
    login(client, unique_email)
    res = client.get("/users/me")
    assert res.status_code == 200
    assert res.json()["email"] == unique_email


def test_logout_clears_session(client, unique_email):
    register(client, unique_email)
    login(client, unique_email)
    res = client.post("/users/logout")
    assert res.status_code == 204
    res = client.get("/users/me")
    assert res.status_code == 401
