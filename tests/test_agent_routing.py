import os
import sys

sys.path.append(os.getcwd())

from app.agents.constants import AgentType
from app.agents.peer import PeerAgent


def test_peer_agent_routes_to_dev():
    agent = PeerAgent()
    agent.llm = None
    decision = agent.route("Write a python script")
    assert decision.agent_type == AgentType.DEV


def test_peer_agent_routes_to_content():
    agent = PeerAgent()
    agent.llm = None
    decision = agent.route("What is the capital of France?")
    assert decision.agent_type == AgentType.CONTENT


def test_peer_agent_fallback_has_reasoning():
    agent = PeerAgent()
    agent.llm = None
    decision = agent.route("Write javascript code")
    assert decision.reasoning is not None
