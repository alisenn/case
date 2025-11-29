from enum import Enum


class AgentType(str, Enum):
    DEV = "dev_agent"
    CONTENT = "content_agent"


AGENT_IDS = [agent.value for agent in AgentType]
