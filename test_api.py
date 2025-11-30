import time
import requests
import pytest

BASE_URL = "http://localhost:8000/v1/agent"
POLL_SECONDS = 45


@pytest.mark.parametrize(
    "task_description",
    [
        "Write a python script named hello.py that prints Hello World",
        "Search for the current price of Bitcoin",
    ],
)
def test_task(task_description):
    response = requests.post(
        f"{BASE_URL}/execute/sync",
        json={"task": task_description}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert isinstance(data.get("result"), str)
