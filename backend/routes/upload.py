# backend/routes/upload.py
from fastapi import APIRouter, UploadFile, File
from encryption.encryptor import encrypt_file
from datetime import datetime, timedelta
import uuid, os

router = APIRouter()
file_db = {}

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()
    encrypted = encrypt_file(content)

    token = str(uuid.uuid4())[:8]
    path = f"uploads/{token}_{file.filename}"

    with open(path, "wb") as f:
        f.write(encrypted)

    file_db[token] = {
        "path": path,
        "filename": file.filename,
        "expires_at": datetime.now().astimezone() + timedelta(minutes=30),
        "downloads_left": 3
    }

    return {
        "download_link": f"http://localhost:8000/download/{token}",
        "expires_at": file_db[token]["expires_at"]
    }
