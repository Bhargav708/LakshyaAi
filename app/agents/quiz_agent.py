from app.agents.llm import get_llm

def generate_quiz(topic: str):
    llm = get_llm()

    prompt = f"""
    Generate 5 multiple choice questions (MCQs) on the topic: {topic}

    Format:
    Q1. Question
    A. Option
    B. Option
    C. Option
    D. Option
    Answer: Correct option

    Keep it clean and structured.
    """

    response = llm.invoke(prompt).content

    return response