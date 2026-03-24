from typing import TypedDict

class AgentState(TypedDict):
    question: str
    response: str
    next: str