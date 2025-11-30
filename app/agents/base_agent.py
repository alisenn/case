from langchain_openai import ChatOpenAI

from app.core.config import settings


class BaseAgent:
    """Shared LLM setup and basic execute behavior for agents."""

    def __init__(self, role: str):
        self.role = role
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL_WORKER,
            temperature=0.2,
            openai_api_key=settings.OPENAI_API_KEY
        ) if settings.OPENAI_API_KEY else None

    def execute(self, task: str) -> str:
        # Base execution for fallback
        if not self.llm:
            return f"[Mock] {self.role} executed task: {task}"
        response = self.llm.invoke(task)
        return response.content
