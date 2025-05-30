# backend/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from backend.routes import upload, download, auth

# Import the database connection functions
from backend.core.database import connect_to_mongo, close_mongo_connection
from backend.core.config import settings # We'll need settings here later for S3 and general config
import os # For ensuring the uploads directory exists


# --- FastAPI Lifespan Events ---
# This context manager handles startup and shutdown logic for the app.
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup Events ---
    print("Application startup initiated...")

    # 1. Ensure 'uploads' directory exists for local encryption/decryption (before S3)
    # This might be temporary if all files move to S3, but good for current state.
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
        print("Created 'uploads/' directory.")

    # 2. Connect to MongoDB
    await connect_to_mongo()
    print("MongoDB connection established.")

    yield # The application will run here

    # --- Shutdown Events ---
    print("Application shutdown initiated...")
    # 1. Close MongoDB connection
    await close_mongo_connection()
    print("MongoDB connection closed.")

# Initialize FastAPI app with the lifespan context manager
app = FastAPI(lifespan=lifespan)

# Include your routers
app.include_router(auth.router)
app.include_router(upload.router)
app.include_router(download.router)