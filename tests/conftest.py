import copy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture
def client() -> TestClient:
    """TestClient for the FastAPI app."""
    return TestClient(app_module.app)


@pytest.fixture(autouse=True)
def reset_activities() -> None:
    """Reset the in-memory activities store after each test.

    The FastAPI app uses a global dict for activities, so tests must not
    leak modifications between each other.
    """

    original = copy.deepcopy(app_module.activities)
    yield
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(original))
