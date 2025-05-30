# backend/routes/upload.py
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from encryption.encryptor import encrypt_file
from datetime import datetime, timedelta
import uuid
# Removed os import as file writing will move to S3 later, but keeping for now for local uploads
import os

# Import the MongoDB collection dependency and the Pydantic model
from motor.motor_asyncio import AsyncIOMotorCollection
from backend.core.database import get_files_collection
from backend.models.file import FileMetadata

router = APIRouter()

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    # Inject the MongoDB collection as a dependency
    files_collection: AsyncIOMotorCollection = Depends(get_files_collection)
):
    # Security: Sanitize filename to prevent path traversal
    # For now, we'll just generate a unique name with the original extension
    # When we move to S3, the "path" will be the S3 key, which is easier to control.
    original_filename = file.filename
    file_extension = os.path.splitext(original_filename)[1] if original_filename else ""
    # Generate a unique token for the file
    token = str(uuid.uuid4())[:8]
    # Create a safe filename for local storage (before S3 integration)
    local_filename = f"{token}{file_extension}"
    path = f"uploads/{local_filename}"


    content = await file.read()
    encrypted = encrypt_file(content)

    try:
        # Save the encrypted file locally (temporarily, until S3 is integrated)
        with open(path, "wb") as f:
            f.write(encrypted)
    except IOError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file locally: {e}"
        )

    # Prepare file metadata for MongoDB
    # s3_key will be the path/key in S3. For now, we'll store the local path here.
    # This will be updated to a proper S3 key in a later step.
    file_metadata = FileMetadata(
        token=token,
        s3_key=path, # Temporarily storing local path here, will be S3 key later
        filename=original_filename,
        expires_at=datetime.now().astimezone() + timedelta(minutes=30),
        downloads_left=3
    )

    try:
        # Insert the file metadata into MongoDB
        result = await files_collection.insert_one(file_metadata.model_dump(by_alias=True))
        # The _id of the inserted document is in result.inserted_id
        print(f"File metadata inserted into MongoDB with ID: {result.inserted_id}")
    except Exception as e:
        # Clean up the locally saved file if DB insertion fails
        if os.path.exists(path):
            os.remove(path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file metadata to database: {e}"
        )


    return {
        "download_link": f"http://localhost:8000/download/{token}",
        "expires_at": file_metadata.expires_at.isoformat() + "Z" # Return in ISO format for clients
    }