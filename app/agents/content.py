from langchain_openai import ChatOpenAI
try:
    from langchain_community.tools import DuckDuckGoSearchRun
    SEARCH_AVAILABLE = True
except ImportError:
    SEARCH_AVAILABLE = False

from app.agents.base import BaseWorker


class ContentAgent(BaseWorker):
    def __init__(self):
        super().__init__("Content Agent")
        if SEARCH_AVAILABLE:
            self.search_tool = DuckDuckGoSearchRun()
        else:
            self.search_tool = None

    def execute(self, task: str) -> str:
        if not self.llm:
            return super().execute(task)
        
        # Simple implementation: If task implies search, use tool.
        # In a full agent, we would use an AgentExecutor.
        # Here we do a manual "Chain" for demonstration.
        try:
            if self.search_tool:
                # 1. Search
                search_results = self.search_tool.run(task)
                # 2. Summarize with LLM (no sources section)
                prompt = (
                    "You are a research assistant. Use ONLY the provided search snippets to answer concisely. "
                    "Do not add a sources section or cite links.\n\n"
                    f"User asked: {task}\n\n"
                    f"Search Results:\n{search_results}\n\n"
                    "Answer:"
                )
                return super().execute(prompt)
            else:
                return super().execute(task)
        except Exception as e:
            return f"Error during search: {str(e)}. Fallback: {super().execute(task)}"
