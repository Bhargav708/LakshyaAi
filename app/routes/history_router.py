from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.model.chat1 import ChatHistory
from app.utils.deps import get_current_user

router = APIRouter()


# ✅ DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ✅ GET HISTORY (FIXED)
@router.get("/history")
def get_history(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)

):
    print("userId :",user_id )
    try:
        # 🔥 Get unique session IDs
        sessions = (
            db.query(ChatHistory.session_id)
            .filter(ChatHistory.user_id == user_id)
            .distinct()
            .all()
        )

        result = []

        for s in sessions:
            session_id = s[0]

            chats = (
                db.query(ChatHistory)
                .filter(
                    ChatHistory.session_id == session_id,
                    ChatHistory.user_id == user_id
                )
                .order_by(ChatHistory.created_at.asc())
                .all()
            )

            if not chats:
                continue

            # 🔥 First and last message
            first = chats[0]
            last = chats[-1]

            result.append({
                "session_id": session_id,
                "type": first.type or "chat",
                "title": first.question or "Untitled",
                "preview": last.answer or "",
                "timestamp": last.created_at.isoformat()
            })

        # 🔥 Sort by latest first (important)
        result.sort(key=lambda x: x["timestamp"], reverse=True)

        return {
            "success": True,
            "history": result   # ✅ directly usable by frontend
        }

    except Exception as e:
        print("ERROR:", e)
        raise HTTPException(status_code=500, detail="Failed to fetch history")


# ✅ DELETE SESSION (FIXED)
@router.delete("/history/{session_id}")
def delete_session(
    session_id: str,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        deleted = (
            db.query(ChatHistory)
            .filter(
                ChatHistory.session_id == session_id,
                ChatHistory.user_id == user_id
            )
            .delete()
        )

        db.commit()

        if deleted == 0:
            raise HTTPException(status_code=404, detail="Session not found")

        return {"success": True}

    except Exception as e:
        print("DELETE ERROR:", e)
        raise HTTPException(status_code=500, detail="Delete failed")