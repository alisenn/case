import os
import sys

sys.path.append(os.getcwd())

from fastapi.testclient import TestClient

from app.agents.constants import AgentType
from app.main import app
from app.services import queue


def test_execute_and_status_eager_mode():
    queue.peer_agent.llm = None
    queue.dev_agent.llm = None
    queue.content_agent.llm = None
    queue._log_to_mongo = lambda _: None

    # Run Celery tasks eagerly in-memory for test determinism
    queue.celery_app.conf.update(
        task_always_eager=True,
        task_store_eager_result=True,
        broker_url="memory://",
        result_backend="cache+memory://",
    )

    client = TestClient(app)

    resp = client.post("/v1/agent/execute", json={"task": "basit bir test gorevi"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "queued"
    assert "task_id" in data

    status_resp = client.get(f"/v1/agent/status/{data['task_id']}")
    assert status_resp.status_code == 200
    status_data = status_resp.json()
    assert status_data["status"] in ("SUCCESS", "completed")
    assert isinstance(status_data.get("result"), dict)
    assert status_data["result"].get("agent") in (AgentType.DEV.value, AgentType.CONTENT.value)
