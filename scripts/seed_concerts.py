"""Seed demo concerts via the running API. Usage: make seed (backend must be up on :8080)."""

import json
import urllib.error
import urllib.request

API_BASE_URL = "http://localhost:8080"

CONCERTS = [
    {"name": "Neon Skyline", "venue": "Riverside Arena", "date": "2026-08-01T19:00:00", "total_seats": 40, "price": 45.0},
    {"name": "Midnight Echoes", "venue": "The Velvet Room", "date": "2026-08-15T20:00:00", "total_seats": 24, "price": 35.0},
    {"name": "Solar Wave Tour", "venue": "Harbor Stage", "date": "2026-09-05T18:30:00", "total_seats": 60, "price": 55.0},
    {"name": "Crimson Static", "venue": "Old Mill Hall", "date": "2026-09-20T19:30:00", "total_seats": 18, "price": 30.0},
    {"name": "Glass Horizon", "venue": "Skyline Pavilion", "date": "2026-10-02T19:00:00", "total_seats": 32, "price": 40.0},
    {"name": "Paper Planets", "venue": "Lower East Hall", "date": "2026-10-18T20:00:00", "total_seats": 50, "price": 38.5},
]


def existing_names() -> set[str]:
    with urllib.request.urlopen(f"{API_BASE_URL}/concerts/") as res:
        return {c["name"] for c in json.loads(res.read())}


def main() -> None:
    seen = existing_names()
    for concert in CONCERTS:
        if concert["name"] in seen:
            print(f"skip (exists): {concert['name']}")
            continue
        req = urllib.request.Request(
            f"{API_BASE_URL}/concerts/",
            data=json.dumps(concert).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req) as res:
                body = json.loads(res.read())
                print(f"created: {body['name']} ({body['id']})")
        except urllib.error.HTTPError as e:
            print(f"failed {concert['name']}: {e.code} {e.read().decode()}")


if __name__ == "__main__":
    main()
