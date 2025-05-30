# backend/routes/auth.py
from fastapi import APIRouter
from jose import jwt
from datetime import datetime, timedelta

router = APIRouter()
SECRET_KEY = "super-secret"

@router.post("/login")
def login(email: str):
    payload = {
        "sub": email,
        "exp": datetime.utcnow() + timedelta(hours=2)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return {"token": token}
