from app.services.celery_app import celery_app
from app.agents.peer import PeerAgent
from app.agents.dev import DevAgent
from app.agents.content import ContentAgent
from app.agents.constants import AgentType
from app.api.models import TaskResult
from app.services.mongo import get_logs_collection

peer_agent = PeerAgent()
dev_agent = DevAgent()
content_agent = ContentAgent()

def _log_to_mongo(task_result: TaskResult):
    try:
        get_logs_collection().insert_one(task_result.model_dump())
    except Exception as log_err:
        # Best-effort logging; do not break task completion if logging fails
        print(f"[Logging] Failed to write task {task_result.task_id} to MongoDB: {log_err}")

@celery_app.task(name="app.services.queue.process_task")
def process_task(task_id: str, task_description: str):
    try:
        # 1. Route
        decision = peer_agent.route(task_description)
        target_agent = decision.agent_type.value if hasattr(decision.agent_type, "value") else decision.agent_type
        
        # 2. Execute
        result_content = ""
        file_path = None
        if target_agent == AgentType.DEV.value:
            result = dev_agent.execute(task_description)
        else:
            result = content_agent.execute(task_description)

        if isinstance(result, dict):
            file_path = result.get("file_path")
            result_content = result.get("message") or result.get("result") or ""
        else:
            result_content = result
            
        # 3. Persist and return
        result = TaskResult(
            task_id=task_id,
            status="completed",
            agent=target_agent,
            result=result_content,
            reasoning=decision.reasoning,
            file_path=file_path
        )
        _log_to_mongo(result)
        return result.model_dump()
    except Exception as e:
        error_result = TaskResult(
            task_id=task_id,
            status="failed",
            error=str(e)
        )
        _log_to_mongo(error_result)
        return error_result.model_dump()
