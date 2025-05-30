# backend/routes/download.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from encryption.encryptor import decrypt_file
from datetime import datetime
import os

router = APIRouter()
from backend.routes.upload import file_db  # temp global use

@router.get("/download/{token}")
def download_file(token: str):
    file_info = file_db.get(token)
    if not file_info:
        raise HTTPException(status_code=404, detail="Invalid token")

    # Check expiry
    if datetime.now(datetime.timezone.utc) > file_info["expires_at"]:
        del file_db[token]
        os.remove(file_info["path"])
        raise HTTPException(status_code=403, detail="Link has expired")

    # Optional: check downloads left
    if file_info["downloads_left"] <= 0:
        del file_db[token]
        os.remove(file_info["path"])
        raise HTTPException(status_code=403, detail="Download limit exceeded")

    # Decrypt
    with open(file_info["path"], "rb") as f:
        encrypted_data = f.read()
    decrypted = decrypt_file(encrypted_data)

    # Decrease download count
    file_info["downloads_left"] -= 1

    return StreamingResponse(
        iter([decrypted]),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{file_info["filename"]}"'}
    )
