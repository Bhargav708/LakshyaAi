from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.graph import graph
from app.crud import save_chat
from app.agents.rag_agent import load_pdf
from app.agents.quiz_agent import generate_quiz

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/ask")
def ask(question: str, user_id: int, db: Session = Depends(get_db)):
    try:
        result = graph.invoke({"question": question})
        answer = result.get("response", "No response")
    except Exception as e:
        answer = f"Error: {str(e)}"

    # Save to DB ALWAYS
    save_chat(db, user_id, question, answer)

    return {"response": answer}

# ✅ NEW QUIZ API
@router.post("/quiz")
def quiz(topic: str, user_id: int, db: Session = Depends(get_db)):
    try:
        quiz_data = generate_quiz(topic)
    except Exception as e:
        quiz_data = f"Error: {str(e)}"

    # Save quiz also in chat history (optional)
    save_chat(db, user_id, f"QUIZ: {topic}", quiz_data)

    return {"quiz": quiz_data}

@router.post("/upload")
def upload(file: UploadFile = File(...)):
    path = f"temp_{file.filename}"

    with open(path, "wb") as f:
        f.write(file.file.read())

    load_pdf(path)

    return {"msg": "PDF indexed"}