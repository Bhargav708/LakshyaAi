from app.agents.llm import get_llm

llm = get_llm()
def chat_agent(state):
    res = llm.invoke(state["question"]).content
    return {"response": res}