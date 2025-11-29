from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from app.agents.constants import AGENT_IDS, AgentType
from app.core.config import settings


class RouteDecision(BaseModel):
    agent_type: AgentType = Field(description=f"The type of agent to route to. Options: {AGENT_IDS}")
    reasoning: str = Field(description="Reason for the routing decision")

class PeerAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL_ROUTER,
            temperature=0,
            openai_api_key=settings.OPENAI_API_KEY
        ) if settings.OPENAI_API_KEY else None
        
        self.parser = PydanticOutputParser(pydantic_object=RouteDecision)
        
        self.prompt = PromptTemplate(
            template="""You are a Peer Agent responsible for routing user tasks to the appropriate worker agent.
            
            Available Agents:
            1. dev_agent: Handles software development tasks, coding, debugging, file manipulation, and technical questions.
            2. content_agent: Handles research, general questions, creative writing, summarization, and non-technical tasks.
            
            Task: {task}
            
            {format_instructions}
            """,
            input_variables=["task"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )

    def route(self, task: str) -> RouteDecision:
        if not self.llm:
            if "python" in task.lower() or "code" in task.lower() or "script" in task.lower():
                return RouteDecision(agent_type=AgentType.DEV, reasoning="Keyword match (fallback)")
            return RouteDecision(agent_type=AgentType.CONTENT, reasoning="Default (fallback)")

        chain = self.prompt | self.llm | self.parser
        return chain.invoke({"task": task})
