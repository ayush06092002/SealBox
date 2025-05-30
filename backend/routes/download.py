# backend/routes/download.py
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import StreamingResponse
from encryption.encryptor import decrypt_file
from datetime import datetime, timezone
import os

# Import MongoDB collection dependency and the Pydantic model
from motor.motor_asyncio import AsyncIOMotorCollection
from backend.core.database import get_files_collection
from backend.models.file import FileMetadata

router = APIRouter()

# REMOVE THIS LINE: from backend.routes.upload import file_db  # temp global use - NO LONGER NEEDED

@router.get("/download/{token}")
async def download_file(
    token: str,
    # Inject the MongoDB collection as a dependency
    files_collection: AsyncIOMotorCollection = Depends(get_files_collection)
):
    # 1. Retrieve file metadata from MongoDB
    # MongoDB stores data as dictionaries, so we'll get a dict back.
    # Convert it to our Pydantic model for type safety and validation.
    file_data_from_db = await files_collection.find_one({"token": token})

    if not file_data_from_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid token or file not found.")

    # Convert the retrieved dictionary to a Pydantic model instance
    try:
        file_info = FileMetadata(**file_data_from_db)
    except Exception as e:
        # This catch is for cases where DB data might be malformed
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Corrupted file metadata in database: {e}"
        )

    # 2. Check expiry
    if datetime.now(timezone.utc) > file_info.expires_at.replace(tzinfo=timezone.utc):
        # Delete from DB and local storage
        await files_collection.delete_one({"token": token})
        if os.path.exists(file_info.s3_key): # s3_key temporarily holds local path
            os.remove(file_info.s3_key)
            print(f"Cleaned up expired file: {file_info.s3_key}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Link has expired.")

    # 3. Check downloads left
    if file_info.downloads_left <= 0:
        # Delete from DB and local storage
        await files_collection.delete_one({"token": token})
        if os.path.exists(file_info.s3_key): # s3_key temporarily holds local path
            os.remove(file_info.s3_key)
            print(f"Cleaned up file due to download limit: {file_info.s3_key}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Download limit exceeded.")

    # 4. Decrypt file (currently from local disk, will be from S3 later)
    try:
        with open(file_info.s3_key, "rb") as f: # s3_key temporarily holds local path
            encrypted_data = f.read()
    except FileNotFoundError:
        # If the DB has info but file is missing on disk
        # Consider deleting from DB here as well
        await files_collection.delete_one({"token": token})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found on server.")
    except IOError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read encrypted file: {e}"
        )

    try:
        decrypted = decrypt_file(encrypted_data)
    except Exception as e: # Catch any decryption errors (e.g., InvalidToken)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to decrypt file. It might be corrupted or encrypted with a different key: {e}"
        )


    # 5. Decrease download count in MongoDB
    new_downloads_left = file_info.downloads_left - 1
    await files_collection.update_one(
        {"token": token},
        {"$set": {"downloads_left": new_downloads_left}}
    )

    # 6. Stream the decrypted file to the client
    return StreamingResponse(
        iter([decrypted]), # Yielding the entire decrypted content as a single chunk
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{file_info.filename}"'}
    )