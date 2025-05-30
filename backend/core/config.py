# backend/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
import os

# Get the directory of the current file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        extra='ignore' # Ignore extra fields in .env not defined in the class
    )

    # Core Application Settings
    APP_NAME: str = "SealBox"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # JWT Authentication Settings
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 2 # 2 hours

    # Encryption Settings
    ENCRYPTION_KEY: str

    # S3 Settings (we will use these in the next steps)
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    AWS_REGION_NAME: str = "ap-south-1" # Example region: Mumbai
    S3_BUCKET_NAME: str | None = None

    # --- MongoDB Settings --- # <-- ADD THESE LINES
    MONGO_DB_URL: str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "sealbox_db"
    MONGO_COLLECTION_NAME: str = "files"

# Create a settings instance that can be imported throughout your application
settings = Settings()

# You can print settings here during development to ensure they are loaded correctly
# print("Loaded Settings:")
# print(f"  App Name: {settings.APP_NAME}")
# print(f"  Environment: {settings.ENVIRONMENT}")
# print(f"  Debug Mode: {settings.DEBUG}")
# print(f"  JWT Secret Key (first 5 chars): {settings.JWT_SECRET_KEY[:5]}...")
# print(f"  Encryption Key (first 5 chars): {settings.ENCRYPTION_KEY[:5]}...")
# print(f"  AWS Region: {settings.AWS_REGION_NAME}")
# print(f"  S3 Bucket: {settings.S3_BUCKET_NAME}")
# print(f"  MongoDB URL: {settings.MONGO_DB_URL}")
# print(f"  MongoDB Name: {settings.MONGO_DB_NAME}")
# print(f"  MongoDB Collection: {settings.MONGO_COLLECTION_NAME}")