"""
MongoDB database connection and utilities
"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings
from contextlib import asynccontextmanager
from typing import Optional
from fastapi import Request

# Global database instance
db_client: Optional[AsyncIOMotorClient] = None
db: Optional[AsyncIOMotorDatabase] = None


async def connect_to_mongo(app):
    """Connect to MongoDB"""
    # global db_client, db
    
    print(f"🔗 Connecting to MongoDB: {settings.MONGODB_URI}")
    
    try:
        db_client = AsyncIOMotorClient(settings.MONGODB_URI)
        # Test connection
        await db_client.admin.command("ping")
        db_client = db_client[settings.MONGODB_DATABASE]
        app.state.db = db_client
        print(f"✅ Successfully connected to MongoDB database: {settings.MONGODB_DATABASE}")
        # return db_client
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        raise


async def close_mongo_connection(app):
    """Close MongoDB connection"""
    # global db_client
    
    if app.state.db is not None:
        print("🔌 Closing MongoDB connection...")
        app.state.db_client.close()
        print("✅ MongoDB connection closed")


def get_db(request: Request):
    # This is the ONLY place that needs to know about the 'request'
    return request.app.state.db

# Collections
async def get_jobs_collection():
    """Get the jobs collection"""
    database = get_db()
    return database["applications"]


async def get_users_collection():
    """Get the users collection"""
    database = get_db()
    return database["users"]


async def get_contacts_collection():
    """Get the contacts collection"""
    database = get_db()
    return database["contacts"]
