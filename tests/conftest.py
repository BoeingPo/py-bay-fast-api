import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def unique_email():
    return f"test-{uuid.uuid4().hex[:12]}@example.com"
