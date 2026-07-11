import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.state.runtime import runtime_state


@pytest.fixture(autouse=True)
def clear_runtime() -> None:
    runtime_state.clear()


@pytest.fixture
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client
