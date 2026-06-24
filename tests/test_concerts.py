def create_concert(client, name, total_seats=10, price=20.0):
    return client.post(
        "/concerts/",
        json={
            "name": name,
            "venue": "Test Hall",
            "date": "2026-12-01T19:00:00",
            "total_seats": total_seats,
            "price": price,
        },
    )


def test_create_and_get_concert(client):
    res = create_concert(client, "Pytest Show")
    assert res.status_code == 201
    body = res.json()
    assert body["available_seats"] == 10

    res = client.get(f"/concerts/{body['id']}")
    assert res.status_code == 200
    assert res.json()["name"] == "Pytest Show"


def test_list_concerts_includes_created(client):
    create_concert(client, "List Test Show")
    res = client.get("/concerts/")
    assert res.status_code == 200
    names = [c["name"] for c in res.json()]
    assert "List Test Show" in names


def test_get_unknown_concert_404(client):
    res = client.get("/concerts/does-not-exist")
    assert res.status_code == 404
