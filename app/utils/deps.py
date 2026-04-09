from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from app.utils.auth import verify_token

security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = verify_token(credentials.credentials)
        return payload["user_id"]
    except HTTPException as e:
        raise HTTPException(status_code=401, detail=f"Invalid or expired token {e} ")