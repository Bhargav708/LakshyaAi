from fastapi import APIRouter, Depends, UploadFile, File, Query
from sqlalchemy.orm import Session
from app.utils.deps import get_current_user
from app.database import SessionLocal
from app.crud import save_chat
from app.agents.rag_agent import load_pdf
from app.agents.quiz_agent import generate_quiz
from app.model.chat1 import ChatHistory
from app.services.file_service import read_file
from app.services.ai_service import summarize_text, chat_with_memory

router = APIRouter()


# ✅ DB CONNECTION
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================================================
# ✅ 1. ASK (WITH MEMORY)
# =========================================================


@router.post("/ask")
def ask(
    question: str,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    history = db.query(ChatHistory).filter(
        ChatHistory.user_id == user_id
    ).all()

    answer = chat_with_memory(question, history)

    save_chat(db, user_id, question, str(answer))

    return {"response": str(answer)}


# =========================================================
# ✅ 2. GET CHAT HISTORY
# =========================================================
@router.get("/history")
def get_history(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    chats = db.query(ChatHistory).filter(
        ChatHistory.user_id == user_id
    ).order_by(ChatHistory.created_at).all()

    return [
        {
            "question": c.question,
            "answer": c.answer,
            "time": c.created_at
        }
        for c in chats
    ]
# =========================================================
# ✅ 3. SUMMARY (FILE → SUMMARY)
# =========================================================
@router.post("/summary")
async def summary(file: UploadFile = File(...)):
    try:
        content = await file.read()
        text = read_file(file.filename, content)

        summary = summarize_text(text)

        return {"summary": str(summary)}

    except Exception as e:
        return {"error": str(e)}


# =========================================================
# ✅ 4. UPLOAD (RAG + SUMMARY)
# =========================================================
@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    try:
        content = await file.read()

        # 📄 Extract text
        text = read_file(file.filename, content)

        # 💾 Save temp file
        path = f"temp_{file.filename}"
        with open(path, "wb") as f:
            f.write(content)

        # 🔍 Load into RAG
        load_pdf(path)

        # 🧠 Generate summary
        summary = summarize_text(text)

        return {
            "filename": file.filename,
            "summary": str(summary),
            "message": "Uploaded + Indexed successfully"
        }

    except Exception as e:
        return {"error": str(e)}


# =========================================================
# ✅ 5. QUIZ GENERATION
# =========================================================
@router.post("/quiz")
def quiz(
    topic: str = Query(...),
    user_id: int = Query(...),
    db: Session = Depends(get_db)
):
    try:
        quiz_data = generate_quiz(topic)

    except Exception as e:
        quiz_data = f"Error: {str(e)}"

    # Save quiz in chat history
    save_chat(db, user_id, f"QUIZ: {topic}", str(quiz_data))

    return {"quiz": str(quiz_data)}