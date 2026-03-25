from app.agents.llm import get_llm

llm = get_llm()


# ✅ SUMMARY
def summarize_text(text: str):
    prompt = f"""
    Summarize the following in simple bullet points for students:

    {text[:3000]}
    """
    return llm.invoke(prompt)


# ✅ CHAT WITH MEMORY
def chat_with_memory(question: str, history: list):
    history_text = ""

    for h in history[-5:]:
        history_text += f"User: {h.question}\nAI: {h.answer}\n"

    prompt = f"""
    You are an AI tutor.

    Previous conversation:
    {history_text}

    Now answer:
    {question}
    """

    return llm.invoke(prompt)