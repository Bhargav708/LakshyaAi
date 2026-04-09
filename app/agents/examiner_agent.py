import json
import PyPDF2
from app.agents.llm import get_llm

llm = get_llm()

# =========================
# 📄 PDF TEXT EXTRACTOR
# =========================
def extract_text_from_pdf(pdf_path: str) -> str:
    text = ""

    try:
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)

            for page in reader.pages:
                text += page.extract_text() or ""

    except Exception as e:
        print("PDF extraction error:", e)
        return ""

    return text.strip()


# =========================
# 📝 TOPIC QUIZ GENERATION
# =========================
def generate_mcqs_from_topic(topic: str, num_questions: int, user_id: int):
    prompt = f"""
You are an expert examiner. 
Generate {num_questions} multiple-choice questions on the topic: "{topic}".

Return ONLY valid JSON:

[
  {{
    "question": "...",
    "options": ["A", "B", "C", "D"],
    "correct_answer": "...",
    "explanation": "...",
    "topic": "{topic}"
  }}
]
"""

    response = llm.invoke(prompt).content

    try:
        mcqs = json.loads(response)
    except Exception as e:
        print("LLM JSON error (topic):", e)

        import random
        mcqs = []
        for i in range(num_questions):
            mcqs.append({
                "question": f"{topic} Q{i+1}",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct_answer": random.choice(["Option A", "Option B", "Option C", "Option D"]),
                "explanation": "Fallback explanation",
                "topic": topic
            })

    return mcqs


# =========================
# 📄 PDF QUIZ GENERATION
# =========================
def generate_mcqs_from_pdf(pdf_path: str, user_id: int):
    text = extract_text_from_pdf(pdf_path)

    if not text:
        raise Exception("❌ Failed to extract text from PDF")

    # ✅ LIMIT TEXT
    text = text[:4000]

    prompt = f"""
You are an expert examiner. 
Generate 5 multiple-choice questions from the following PDF content.

Return ONLY valid JSON:

[
  {{
    "question": "...",
    "options": ["A", "B", "C", "D"],
    "correct_answer": "...",
    "explanation": "...",
    "topic": "PDF Topic"
  }}
]

PDF CONTENT:
{text}
"""

    response = llm.invoke(prompt).content

    try:
        mcqs = json.loads(response)
    except Exception as e:
        print("LLM JSON error (pdf):", e)

        import random
        mcqs = []
        for i in range(5):
            mcqs.append({
                "question": f"PDF Q{i+1}",
                "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
                "correct_answer": random.choice(["Option 1", "Option 2", "Option 3", "Option 4"]),
                "explanation": "Fallback explanation",
                "topic": "PDF Topic"
            })

    return mcqs