from fastapi import APIRouter, UploadFile, File, Depends
from pydantic import BaseModel
from typing import List
import os

from sqlalchemy.orm import Session
from app.database import SessionLocal

from app.utils.deps import get_current_user
from app.utils.session import create_session_id
from app.crud import save_chat
from app.agents.examiner_agent import generate_mcqs_from_topic, generate_mcqs_from_pdf

router = APIRouter()

# =========================
# DB Dependency
# =========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# 📄 Upload PDF for Quiz
# =========================
@router.post("/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    content = await file.read()
    os.makedirs("uploads", exist_ok=True)

    path = f"uploads/{user_id}_{file.filename}"
    with open(path, "wb") as f:
        f.write(content)

    # Generate MCQs
    mcqs_raw = generate_mcqs_from_pdf(path, user_id)

    mcqs = [
        {
            "id": idx + 1,
            "question": q["question"],
            "options": q["options"],
            "correct": q["options"].index(q["correct_answer"]),
            "explanation": q.get("explanation", "No explanation provided."),
            "topic": q.get("topic", "PDF Topic")
        }
        for idx, q in enumerate(mcqs_raw)
    ]

    session_id = create_session_id()

    # ✅ SAVE PDF QUIZ
    save_chat(
        db,
        user_id,
        f"PDF Quiz: {file.filename}",
        "Generated MCQs from PDF",
        session_id,
        "pdf_quiz",
        metadata={"mcqs": mcqs}
    )

    return {"success": True, "session_id": session_id, "mcqs": mcqs}


# =========================
# 📝 Generate MCQs from Topic
# =========================
class TopicRequest(BaseModel):
    topic: str
    num_questions: int = 10
    difficulty: str = "medium"
    session_id: str | None = None


@router.post("/generate")
def generate_quiz(
    req: TopicRequest,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session_id = req.session_id or create_session_id()

    mcqs_raw = generate_mcqs_from_topic(req.topic, req.num_questions, user_id)

    mcqs = [
        {
            "id": idx + 1,
            "question": q["question"],
            "options": q["options"],
            "correct": q["options"].index(q["correct_answer"]),
            "explanation": q.get("explanation", "No explanation provided."),
            "topic": q.get("topic", req.topic)
        }
        for idx, q in enumerate(mcqs_raw)
    ]

    # ✅ SAVE QUIZ
    save_chat(
        db,
        user_id,
        f"Quiz on {req.topic}",
        "Quiz Generated",
        session_id,
        "quiz",
        metadata={"mcqs": mcqs}
    )

    return {"success": True, "session_id": session_id, "mcqs": mcqs}


# =========================
# ✅ Submit Quiz
# =========================
class QuizAttempt(BaseModel):
    mcqs: List[dict]
    answers: List[int]
    session_id: str


@router.post("/submit")
def submit_quiz(
    attempt: QuizAttempt,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    total = len(attempt.mcqs)
    score = 0
    weak_topics = []
    detailed_results = []

    for i, q in enumerate(attempt.mcqs):
        user_ans = attempt.answers[i] if i < len(attempt.answers) else None
        is_correct = user_ans == q.get("correct")

        if is_correct:
            score += 1
        else:
            weak_topics.append(q.get("topic", "General"))

        detailed_results.append({
            "id": q["id"],
            "question": q["question"],
            "options": q["options"],
            "correct": q["correct"],
            "user_answer": user_ans,
            "explanation": q.get("explanation", "No explanation provided."),
            "topic": q.get("topic", "General")
        })

    percentage = (score / total) * 100 if total else 0

    unique_weak_topics = sorted(set(weak_topics))

    feedback = (
        f"Weak areas: {', '.join(unique_weak_topics)}"
        if unique_weak_topics
        else "Excellent! No weak areas."
    )

    # ✅ DEFINE RESULT DATA (FIXED)
    result_data = {
        "score": score,
        "total": total,
        "percentage": percentage,
        "weak_topics": unique_weak_topics
    }

    # ✅ SAVE RESULT TO DB
    save_chat(
        db,
        user_id,
        "Quiz Submission",
        f"Score: {score}/{total}",
        attempt.session_id,
        "quiz_result",
        metadata=result_data
    )

    return {
        "success": True,
        "score": score,
        "total": total,
        "percentage": percentage,
        "feedback": feedback,
        "results": detailed_results
    }