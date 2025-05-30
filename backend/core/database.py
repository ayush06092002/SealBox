# backend/core/database.py
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from backend.core.config import settings

# Global variables for the MongoDB client and database
# These will be initialized in main.py's lifespan events
client: AsyncIOMotorClient = None
db = None

# Dependency function to get the MongoDB collection
async def get_files_collection() -> AsyncIOMotorCollection:
    """
    Dependency that provides access to the MongoDB 'files' collection.
    """
    if client is None or db is None:
        raise ConnectionError("MongoDB client not initialized.")
    return db[settings.MONGO_COLLECTION_NAME]

# Lifespan events for FastAPI application startup and shutdown
async def connect_to_mongo():
    """
    Connects to MongoDB and initializes the global client and database objects.
    """
    global client, db
    try:
        client = AsyncIOMotorClient(settings.MONGO_DB_URL,
                                    uuidRepresentation='standard') # For consistent UUID handling
        db = client[settings.MONGO_DB_NAME]
        # Optional: Ping the database to ensure connection
        await db.command('ping')
        print("Connected to MongoDB!")
    except Exception as e:
        print(f"Could not connect to MongoDB: {e}")
        # In a real app, you might want to exit or raise a critical error
        raise

async def close_mongo_connection():
    """
    Closes the MongoDB client connection.
    """
    global client
    if client:
        client.close()
        print("Disconnected from MongoDB.")