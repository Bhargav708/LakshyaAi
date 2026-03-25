from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.model.user import User
from app.utils.hash import hash_password, verify_password
from app.utils.auth import create_token

router = APIRouter(prefix="/auth")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ✅ REGISTER
@router.post("/register")
def register(name: str, email: str, password: str, db: Session = Depends(get_db)):

    # check existing user
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return {"error": "Email already registered"}

    user = User(
        name=name,   # ✅ ADD NAME HERE
        email=email,
        password=hash_password(password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "msg": "User created",
        "user_id": user.id,
        "name": user.name
    }


# ✅ LOGIN
@router.post("/login")
def login(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(password, user.password):
        return {"error": "Invalid credentials"}

    token = create_token(user.id)

    return {
        "token": token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    }