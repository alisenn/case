from pydantic import BaseModel, Field, constr
from typing import Optional, Any

class TaskRequest(BaseModel):
    task: constr(strip_whitespace=True, min_length=1) = Field(..., description="The task description provided by the user.")

class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str

class TaskResult(BaseModel):
    task_id: str
    status: str
    result: Optional[Any] = None
    agent: Optional[str] = None
    reasoning: Optional[str] = None
    file_path: Optional[str] = None
    error: Optional[str] = None
