# backend/core/s3.py
from aiobotocore.session import get_session
from typing import AsyncGenerator
from backend.core.config import settings
from botocore.client import BaseClient as S3Client
# import asyncio # No longer strictly needed here, unless you had other async ops in lifespan

# Global variable for the S3 client
# It's crucial this is initially None and set within connect_to_s3
s3_client_instance = None # Renamed to avoid confusion with the module itself

# Lifespan events for S3 client connection and disconnection
async def connect_to_s3():
    """
    Connects to AWS S3 and initializes the global s3_client_instance.
    """
    global s3_client_instance # Make sure we're modifying the global variable
    session = get_session()
    try:
        # Correct way to get the S3 client from aiobotocore
        # 'async with' enters the context manager and yields the actual client
        s3_client_instance = await session.create_client(
            "s3",
            region_name=settings.AWS_REGION_NAME,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        ).__aenter__() # Manually call __aenter__ to get the client from the context manager

        # Test connection by listing buckets (or a specific bucket)
        # This will raise an exception if credentials/region are wrong or access denied
        await s3_client_instance.list_buckets() # Now this should work on the actual client
        print(f"Connected to AWS S3 in region {settings.AWS_REGION_NAME}")

    except Exception as e:
        print(f"Could not connect to AWS S3: {e}")
        # Ensure the client is closed if connection fails during setup
        if s3_client_instance:
            await s3_client_instance.close()
            s3_client_instance = None # Reset to None if connection failed
        raise # Re-raise the exception to stop startup if connection failed

async def close_s3_connection():
    """
    Closes the AWS S3 client connection.
    """
    global s3_client_instance
    if s3_client_instance:
        await s3_client_instance.close()
        s3_client_instance = None # Reset to None after closing
        print("Disconnected from AWS S3.")

# Dependency for getting the S3 client
async def get_s3_client() -> AsyncGenerator[S3Client, None]:
    """
    Dependency that provides access to the AWS S3 client.
    """
    # Ensure the client is initialized before yielding it
    if s3_client_instance is None:
        # This should ideally not happen if lifespan connect_to_s3 works
        raise ConnectionError("S3 client not initialized. Check AWS credentials and bucket settings.")
    yield s3_client_instance