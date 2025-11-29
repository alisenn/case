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
        f"{BASE_URL}/execute",
        json={"task": task_description}
    )
    assert response.status_code == 200
    data = response.json()
    task_id = data["task_id"]
    assert data["status"] == "queued"

    # Poll for result
    final_status = None
    result_payload = None
    for _ in range(POLL_SECONDS):
        status_res = requests.get(f"{BASE_URL}/status/{task_id}")
        assert status_res.status_code == 200
        status_data = status_res.json()
        final_status = status_data["status"]
        result_payload = status_data.get("result")
        if final_status in ("SUCCESS", "FAILURE", "completed"):
            break
        time.sleep(1)

    assert final_status in ("SUCCESS", "completed")
    assert isinstance(result_payload, dict)
