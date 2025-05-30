# backend/routes/download.py
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import StreamingResponse
from encryption.encryptor import decrypt_file
from datetime import datetime, timezone
import os # Keep os for path manipulation, though local file ops will be removed

# Import MongoDB collection dependency and the Pydantic model
from motor.motor_asyncio import AsyncIOMotorCollection
from backend.core.database import get_files_collection
from backend.models.file import FileMetadata

# Import S3 client dependency and S3 bucket settings
from botocore.client import BaseClient as S3Client # Corrected import for S3Client type hint
from backend.core.s3 import get_s3_client
from backend.core.config import settings

router = APIRouter()

@router.get("/download/{token}")
async def download_file(
    token: str,
    files_collection: AsyncIOMotorCollection = Depends(get_files_collection),
    s3_client: S3Client = Depends(get_s3_client) # Inject the S3 client
):
    # 1. Retrieve file metadata from MongoDB
    file_data_from_db = await files_collection.find_one({"token": token})

    if not file_data_from_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid token or file not found.")

    try:
        file_info = FileMetadata(**file_data_from_db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Corrupted file metadata in database: {e}"
        )

    # 2. Check expiry and downloads left
    is_expired = datetime.now(timezone.utc) > file_info.expires_at.replace(tzinfo=timezone.utc)
    is_download_limit_exceeded = file_info.downloads_left <= 0

    if is_expired or is_download_limit_exceeded:
        # Delete from DB and S3
        await files_collection.delete_one({"token": token})
        try:
            await s3_client.delete_object(Bucket=settings.S3_BUCKET_NAME, Key=file_info.s3_key)
            print(f"Cleaned up S3 object: {file_info.s3_key} due to {'expiry' if is_expired else 'download limit'}.")
        except Exception as s3_del_e:
            print(f"Failed to delete S3 object {file_info.s3_key}: {s3_del_e}")
            # Do not re-raise, as the primary goal (preventing download) is met.

        if is_expired:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Link has expired.")
        else: # Must be download limit exceeded
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Download limit exceeded.")

    # 3. Download encrypted file from S3
    encrypted_data = None
    try:
        # Use get_object to download from S3
        response = await s3_client.get_object(Bucket=settings.S3_BUCKET_NAME, Key=file_info.s3_key)
        async with response['Body'] as stream:
            encrypted_data = await stream.read() # Read the entire object body
        print(f"File '{file_info.filename}' downloaded from S3 at key: {file_info.s3_key}")
    except s3_client.exceptions.NoSuchKey:
        # This occurs if the S3 object somehow doesn't exist, but DB entry does
        await files_collection.delete_one({"token": token}) # Clean up DB
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found in storage.")
    except Exception as e:
        print(f"S3 download error for key {file_info.s3_key}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve file from storage: {e}"
        )

    # 4. Decrypt file
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