"""
Database operations helper functions for Job Applications
"""
from app.db_processor import get_jobs_collection, get_users_collection
from app.models import JobApplication, JobApplicationCreate, JobApplicationUpdate, User, UserCreate
from bson import ObjectId
from typing import List, Optional
import bcrypt


async def create_user(user_data: UserCreate, db) -> dict:
    """Create a new user with hashed password"""
    # collection = await get_users_collection()
    collection = db["users"]
    
    # Check if user already exists
    existing = await collection.find_one({"userid": user_data.userid})
    if existing:
        return {"error": "User already exists"}
    
    # Hash password
    hashed = bcrypt.hashpw(user_data.password.encode('utf-8'), bcrypt.gensalt())
    
    user_dict = {
        "userid": user_data.userid,
        "hashed_password": hashed.decode('utf-8')
    }
    
    result = await collection.insert_one(user_dict)
    return {
        "id": str(result.inserted_id),
        "message": "User created successfully"
    }


async def authenticate_user(userid: str, password: str, db) -> Optional[dict]:
    """Authenticate user"""
    collection = db["users"]
    user = await collection.find_one({"userid": userid})
    if not user:
        return None
    
    if bcrypt.checkpw(password.encode('utf-8'), user["hashed_password"].encode('utf-8')):
        return {"userid": user["userid"], "id": str(user["_id"])}
    return None


async def create_job(job_data: JobApplicationCreate, db) -> dict:
    """Create a new job application"""
    collection = db["applications"]
    job_dict = job_data.model_dump(exclude_none=True)
    
    result = await collection.insert_one(job_dict)
    return {
        "id": str(result.inserted_id),
        "message": "Job application created successfully"
    }


async def get_jobs(
    db,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    platform: Optional[str] = None
) -> List[dict]:
    """Get job applications with optional filtering"""
    collection = db["applications"]
    
    query = {}
    if status:
        query["status"] = status
    if platform:
        query["platform"] = platform
    
    applications = await collection.find(query).skip(skip).limit(limit).to_list(limit)
    
    # Convert ObjectId to string for JSON serialization
    for app in applications:
        if "_id" in app:
            app["_id"] = str(app["_id"])
    
    return applications


async def get_job_by_id(job_id: str, db) -> Optional[dict]:
    """Get a specific job application by ID"""
    # collection = await get_jobs_collection()  
    collection = db["applications"]
    try:
        application = await collection.find_one({"_id": ObjectId(job_id)})
        if application:
            application["_id"] = str(application["_id"])
        return application
    except Exception:
        return None


async def update_job(job_id: str, job_data: JobApplicationUpdate, db) -> dict:
    """Update a job application"""
    collection = db["applications"]
    
    try:
        update_dict = job_data.dict(exclude_none=True)
        
        result = await collection.update_one(
            {"_id": ObjectId(job_id)},
            {"$set": update_dict}
        )
        
        if result.matched_count == 0:
            return {"error": "Job application not found"}
        
        return {"message": "Job application updated successfully"}
    except Exception as e:
        return {"error": str(e)}


async def delete_job(job_id: str, db) -> dict:
    """Delete a job application"""
    collection = db["applications"]
    
    try:
        result = await collection.delete_one({"_id": ObjectId(job_id)})
        
        if result.deleted_count == 0:
            return {"error": "Job application not found"}
        
        return {"message": "Job application deleted successfully"}
    except Exception as e:
        return {"error": str(e)}


async def get_stats() -> dict:
    """Get statistics about job applications"""
    collection = db["applications"]
    
    total = await collection.count_documents({})
    by_status = {}
    
    statuses = ["applied", "screening", "interview", "technical", "offer", "rejected", "ghosted"]
    for status in statuses:
        count = await collection.count_documents({"status": status})
        by_status[status] = count
    
    by_platform = {}
    platforms = await collection.distinct("platform")
    for platform in platforms:
        count = await collection.count_documents({"platform": platform})
        by_platform[platform] = count
    
    return {
        "total": total,
        "by_status": by_status,
        "by_platform": by_platform
    }