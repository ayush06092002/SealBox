# backend/models/file.py
from pydantic import BaseModel, Field, BeforeValidator
from typing import Optional, Annotated
from datetime import datetime
from bson import ObjectId

# Custom type for handling MongoDB's ObjectId
# This allows Pydantic to validate ObjectId as a string, but converts to ObjectId when needed
PyObjectId = Annotated[str, BeforeValidator(str)]

class FileMetadata(BaseModel):
    """
    Pydantic model for file metadata stored in MongoDB.
    """
    # MongoDB's default primary key "_id"
    # It's Optional because MongoDB generates it on insert.
    id: Optional[PyObjectId] = Field(alias="_id", default=None)

    token: str = Field(..., min_length=8, max_length=8) # Ensure token is 8 chars
    s3_key: str # The key under which the file is stored in S3 (replaces 'path')
    filename: str
    expires_at: datetime
    downloads_left: int = Field(..., ge=0) # Must be greater than or equal to 0

    class Config:
        populate_by_name = True # Allow population by field name or alias
        arbitrary_types_allowed = True # Allow ObjectId type
        json_schema_extra = {
            "example": {
                "token": "abcdefg1",
                "s3_key": "uploads/abcdefg1_my_document.pdf",
                "filename": "my_document.pdf",
                "expires_at": "2025-12-31T23:59:59Z",
                "downloads_left": 3
            }
        }