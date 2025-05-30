# backend/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
import os

# Get the directory of the current file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Settings(BaseSettings):
    # This tells Pydantic Settings where to look for the .env file
    # It will look in the current working directory, and also in the directory where this config.py file is.
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        extra='ignore' # Ignore extra fields in .env not defined in the class
    )

    # Core Application Settings
    APP_NAME: str = "SealBox"
    ENVIRONMENT: str = "development" # e.g., 'development', 'staging', 'production'
    DEBUG: bool = True

    # JWT Authentication Settings
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 2 # 2 hours

    # Encryption Settings
    ENCRYPTION_KEY: str # This will be your Fernet key

    # S3 Settings (we will use these in the next steps)
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    AWS_REGION_NAME: str = "ap-south-1" # Example region: Mumbai
    S3_BUCKET_NAME: str | None = None

    # Database Settings (we will use these later)
    DATABASE_URL: str = "sqlite:///./sql_app.db" # Default to SQLite for easy local dev

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
# print(f"  Database URL: {settings.DATABASE_URL}")