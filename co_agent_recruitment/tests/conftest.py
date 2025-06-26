import pytest
import os

@pytest.fixture(scope="function", autouse=True)
def set_test_environment(monkeypatch):
    """Set environment variables for the test session."""
    monkeypatch.setenv("PROJECT_ID", "test-project-id")
