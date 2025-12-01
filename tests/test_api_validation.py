import os
import sys
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

sys.path.append(os.getcwd())

from app.main import app


@pytest.fixture(autouse=True)
def mock_celery_delay():
    with patch("app.api.routes.process_task") as mock_task:
        mock_async_result = MagicMock()
        mock_async_result.id = "test-task-id"
        mock_task.apply_async.return_value = mock_async_result
        yield mock_task


client = TestClient(app)


def test_api_execute_queued():
    response = client.post("/v1/agent/execute", json={"task": "Write a python hello world"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "queued"
    assert "task_id" in data


def test_rejects_empty_task():
    response = client.post("/v1/agent/execute", json={"task": "   "})
    assert response.status_code in (400, 422)


def test_rejects_missing_task_field():
    response = client.post("/v1/agent/execute", json={})
    assert response.status_code == 422


def test_rejects_null_task():
    response = client.post("/v1/agent/execute", json={"task": None})
    assert response.status_code == 422


def test_rejects_invalid_task_type():
    response = client.post("/v1/agent/execute", json={"task": 12345})
    assert response.status_code == 422


def test_rejects_invalid_json():
    response = client.post(
        "/v1/agent/execute",
        content="not valid json",
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 422


def test_handles_unicode_task():
    response = client.post("/v1/agent/execute", json={"task": "Python ile Turkce dosya yaz"})
    assert response.status_code == 200
