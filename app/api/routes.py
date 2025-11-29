import logging
import uuid

from celery.result import AsyncResult
from fastapi import APIRouter, HTTPException

from app.api.models import TaskRequest, TaskResponse, TaskResult
from app.services.celery_app import celery_app
from app.services.queue import process_task

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/execute", response_model=TaskResponse)
async def execute_task(request: TaskRequest):
    """Submit a task for async processing via Celery queue."""
    if not request.task or not request.task.strip():
        raise HTTPException(status_code=400, detail="Task cannot be empty")

    task_id = str(uuid.uuid4())
    
    try:
        # Async queue - task processed by Celery worker
        process_task.apply_async(args=[task_id, request.task], task_id=task_id)
        logger.info(f"Task {task_id} queued")
    except Exception as exc:
        logger.error(f"Failed to queue task: {exc}")
        raise HTTPException(status_code=500, detail="Failed to queue task")
    
    return TaskResponse(
        task_id=task_id,
        status="queued",
        message="Task queued. Check status via GET /status/{task_id}"
    )


@router.post("/execute/sync", response_model=TaskResult)
async def execute_task_sync(request: TaskRequest):
    """Execute task synchronously (for testing)."""
    if not request.task or not request.task.strip():
        raise HTTPException(status_code=400, detail="Task cannot be empty")

    task_id = str(uuid.uuid4())
    
    try:
        result = process_task(task_id, request.task)
        return result
    except Exception as exc:
        logger.error(f"Task failed: {exc}")
        raise HTTPException(status_code=500, detail=f"Task failed: {exc}")


@router.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """Get status and result of a queued task."""
    task_result = AsyncResult(task_id, app=celery_app)
    
    return {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result if task_result.status == "SUCCESS" else None,
        "error": str(task_result.result) if task_result.status == "FAILURE" else None
    }
