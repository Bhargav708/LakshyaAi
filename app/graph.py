from langgraph.graph import StateGraph, END
from app.state import AgentState

from app.agents.supervisor import supervisor
from app.agents.chat_agent import chat_agent
from app.agents.quiz_agent import generate_quiz
from app.agents.rag_agent import rag_agent

builder = StateGraph(AgentState)

builder.add_node("supervisor", supervisor)
builder.add_node("chat", chat_agent)
builder.add_node("quiz", generate_quiz)
builder.add_node("rag", rag_agent)

builder.set_entry_point("supervisor")

def route(state):
    return state["next"]

builder.add_conditional_edges(
    "supervisor",
    route,
    {
        "chat": "chat",
        "quiz": "quiz",
        "rag": "rag"
    }
)

builder.add_edge("chat", END)
builder.add_edge("quiz", END)
builder.add_edge("rag", END)

graph = builder.compile()