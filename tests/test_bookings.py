import pytest

from tests.test_concerts import create_concert
from tests.test_users import login, register


@pytest.fixture
def authed_client(client, unique_email):
    register(client, unique_email)
    res = login(client, unique_email)
    return client, res.json()["id"]


@pytest.fixture
def concert(client):
    return create_concert(client, "Booking Test Show", total_seats=5, price=10.0).json()


def test_book_seats_decrements_availability(authed_client, concert):
    client, _ = authed_client
    res = client.post(f"/concerts/{concert['id']}/book", json={"seats_count": 2})
    assert res.status_code == 201
    booking = res.json()
    assert booking["seats_count"] == 2
    assert booking["status"] == "confirmed"

    res = client.get(f"/concerts/{concert['id']}")
    assert res.json()["available_seats"] == 3


def test_book_more_than_available_rejected(authed_client, concert):
    client, _ = authed_client
    res = client.post(f"/concerts/{concert['id']}/book", json={"seats_count": 99})
    assert res.status_code == 409


def test_book_requires_authentication(client, concert):
    res = client.post(f"/concerts/{concert['id']}/book", json={"seats_count": 1})
    assert res.status_code == 401


def test_cancel_booking_restores_seats(authed_client, concert):
    client, _ = authed_client
    res = client.post(f"/concerts/{concert['id']}/book", json={"seats_count": 2})
    booking_id = res.json()["id"]

    res = client.delete(f"/bookings/{booking_id}")
    assert res.status_code == 204

    res = client.get(f"/concerts/{concert['id']}")
    assert res.json()["available_seats"] == 5

    res = client.get(f"/bookings/{booking_id}")
    assert res.json()["status"] == "cancelled"


def test_cancel_already_cancelled_booking_rejected(authed_client, concert):
    client, _ = authed_client
    res = client.post(f"/concerts/{concert['id']}/book", json={"seats_count": 1})
    booking_id = res.json()["id"]
    client.delete(f"/bookings/{booking_id}")

    res = client.delete(f"/bookings/{booking_id}")
    assert res.status_code == 409


def test_list_bookings_filters_by_user(authed_client, concert):
    client, user_id = authed_client
    client.post(f"/concerts/{concert['id']}/book", json={"seats_count": 1})

    res = client.get(f"/bookings/?user_id={user_id}")
    assert res.status_code == 200
    bookings = res.json()
    assert len(bookings) >= 1
    assert all(b["user_id"] == user_id for b in bookings)
