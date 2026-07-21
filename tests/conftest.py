"""
conftest.py is pytest's special file for shared fixtures — pytest auto-discovers it, so any test can just name 'client' as an argument and get it (no import needed). That's the reusable-fixtures pattern.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

@pytest.fixture
def client() -> TestClient:
    return TestClient(app=app)

