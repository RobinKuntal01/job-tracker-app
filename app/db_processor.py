"""
MongoDB database connection and utilities
"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings
from contextlib import asynccontextmanager
from typing import Optional

# Global database instance
db_client: Optional[AsyncIOMotorClient] = None
db: Optional[AsyncIOMotorDatabase] = None


async def connect_to_mongo():
    """Connect to MongoDB"""
    global db_client, db
    
    print(f"🔗 Connecting to MongoDB: {settings.MONGODB_URI}")
    
    try:
        db_client = AsyncIOMotorClient(settings.MONGODB_URI)
        # Test connection
        await db_client.admin.command("ping")
        db = db_client[settings.MONGODB_DATABASE]
        print(f"✅ Successfully connected to MongoDB database: {settings.MONGODB_DATABASE}")
        return db
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        raise


async def close_mongo_connection():
    """Close MongoDB connection"""
    global db_client
    
    if db_client:
        print("🔌 Closing MongoDB connection...")
        db_client.close()
        print("✅ MongoDB connection closed")


def get_database() -> AsyncDatabase:
    """Get the database instance"""
    if db is None:
        raise RuntimeError("Database not initialized. Call connect_to_mongo() first.")
    return db


# Collections
async def get_jobs_collection():
    """Get the jobs collection"""
    database = get_database()
    return database["applications"]


async def get_users_collection():
    """Get the users collection"""
    database = get_database()
    return database["users"]


async def get_contacts_collection():
    """Get the contacts collection"""
    database = get_database()
    return database["contacts"]
