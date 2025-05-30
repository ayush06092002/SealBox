# backend/routes/upload.py
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from encryption.encryptor import encrypt_file
from datetime import datetime, timedelta, timezone
import uuid
import os # Keep os for path manipulation, though local file saving will be removed

# Import MongoDB collection dependency and the Pydantic model
from motor.motor_asyncio import AsyncIOMotorCollection
from backend.core.database import get_files_collection
from backend.models.file import FileMetadata

# Import S3 client dependency and S3 bucket settings
from aiobotocore.client import BaseClient as S3Client # Type hint for the S3 client
from backend.core.s3 import get_s3_client
from backend.core.config import settings

router = APIRouter()

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    files_collection: AsyncIOMotorCollection = Depends(get_files_collection),
    s3_client: S3Client = Depends(get_s3_client) # Inject the S3 client
):
    original_filename = file.filename
    file_extension = os.path.splitext(original_filename)[1] if original_filename else ""
    token = str(uuid.uuid4())[:8]

    # --- S3 Key Generation ---
    # The s3_key is the unique identifier for the object in the S3 bucket.
    # It replaces the local 'path'.
    s3_key = f"files/{token}{file_extension}" # Example: 'files/abcdefg1.pdf'

    content = await file.read()
    encrypted_content = encrypt_file(content)

    # --- Upload Encrypted File to S3 ---
    try:
        await s3_client.put_object(
            Bucket=settings.S3_BUCKET_NAME,
            Key=s3_key,
            Body=encrypted_content,
            ContentType="application/octet-stream" # Or file.content_type if you want to be specific
        )
        print(f"File '{original_filename}' uploaded to S3 at key: {s3_key}")
    except Exception as e:
        # Catch S3 specific errors and provide a clear message
        print(f"S3 upload error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file to storage: {e}"
        )

    # --- IMPORTANT: Remove Local File Saving ---
    # The following lines are no longer needed as files are directly uploaded to S3.
    # if os.path.exists(path):
    #     os.remove(path)


    # Prepare file metadata for MongoDB, now using s3_key
    file_metadata = FileMetadata(
        token=token,
        s3_key=s3_key, # Store the S3 key in the database
        filename=original_filename,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES), # Using setting
        downloads_left=3 # Or make this configurable via settings too
    )

    try:
        await files_collection.insert_one(file_metadata.model_dump(by_alias=True, exclude_none=True))
        print(f"File metadata inserted into MongoDB for token: {token}")
    except Exception as e:
        # If DB insertion fails, attempt to delete the file from S3 to avoid orphaned files
        try:
            await s3_client.delete_object(Bucket=settings.S3_BUCKET_NAME, Key=s3_key)
            print(f"Cleaned up S3 object {s3_key} due to DB insertion failure.")
        except Exception as s3_del_e:
            print(f"Failed to clean up S3 object {s3_key} after DB insertion failure: {s3_del_e}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file metadata to database: {e}"
        )

    return {
        "download_link": f"http://localhost:8000/download/{token}",
        "expires_at": file_metadata.expires_at.isoformat() + "Z"
    }