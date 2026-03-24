from app.agents.llm import get_llm

def supervisor(state):
    llm = get_llm()

    q = state["question"]

    prompt = f"""
    You are an AI router.

    Choose ONLY ONE:
    chat | quiz | rag

    Question: {q}
    """

    decision = llm.invoke(prompt).content.strip().lower()

    return {"next": decision}