# backend/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from backend.routes import upload, download, auth

# Import the database connection functions (MongoDB)
from backend.core.database import connect_to_mongo, close_mongo_connection

# Import the S3 connection functions
from backend.core.s3 import connect_to_s3, close_s3_connection

from backend.core.config import settings # We'll need settings here later for S3 and general config
import os # For ensuring the uploads directory exists (will be removed soon)


# --- FastAPI Lifespan Events ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup Events ---
    print("Application startup initiated...")

    # 1. Connect to MongoDB
    await connect_to_mongo()
    print("MongoDB connection established.")

    # 2. Connect to S3
    await connect_to_s3()
    print("S3 connection established.")

    yield # The application will run here

    # --- Shutdown Events ---
    print("Application shutdown initiated...")
    # 1. Close S3 connection
    await close_s3_connection()
    print("S3 connection closed.")

    # 2. Close MongoDB connection
    await close_mongo_connection()
    print("MongoDB connection closed.")


# Initialize FastAPI app with the lifespan context manager
app = FastAPI(lifespan=lifespan)

# Include your routers
app.include_router(auth.router)
app.include_router(upload.router)
app.include_router(download.router)