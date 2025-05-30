# backend/routes/auth.py
from fastapi import APIRouter
from jose import jwt
from datetime import datetime, timedelta

from backend.core.config import settings # Import your settings

router = APIRouter()

# Use the secret key and algorithm from settings
SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM # Define ALGORITHM as well

@router.post("/login")
def login(email: str):
    # In a real app, you'd verify email/password against a DB here.
    # For now, it still issues a token for any email.

    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": email,
        "exp": datetime.now().astimezone + expires_delta
    }
    # Use the algorithm from settings
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return {"token": token}