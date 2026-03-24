# MongoDB Setup Guide

## Installation

The MongoDB dependencies have been installed:
- **motor**: Async MongoDB driver for Python
- **pymongo[srv]**: MongoDB Python driver with SRV support
- **pydantic-settings**: For environment variable configuration

## Configuration

### 1. Create `.env` file

Copy `.env.example` to `.env` and update your MongoDB connection URI:

```bash
cp .env.example .env
```

### 2. MongoDB URI Options

#### Local MongoDB:
```
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=job_tracker
```

#### MongoDB Atlas (Cloud):
```
MONGODB_URI=mongodb+srv://your_username:your_password@your_cluster.mongodb.net
MONGODB_DATABASE=job_tracker
```

## Database Structure

The application uses MongoDB collections:

### Collections:
- **applications**: Stores job applications
- **contacts**: Stores LinkedIn contacts (optional, currently managed via applications)

### Document Schema

#### Job Application Document:
```json
{
  "_id": ObjectId,
  "company": "string",
  "role": "string",
  "platform": "string (LinkedIn, Naukri, Indeed, etc.)",
  "status": "string (applied, screening, interview, technical, offer, rejected, ghosted)",
  "date": "string (ISO date)",
  "url": "string (job posting URL)",
  "notes": "string",
  "contacts": [
    {
      "name": "string",
      "dept": "string",
      "role": "string",
      "status": "string (not-sent, requested, connected)"
    }
  ],
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

## How It Works

### Startup
- FastAPI automatically connects to MongoDB on startup via the lifespan context manager
- Connection status is logged to console

### Shutdown
- MongoDB connection is properly closed when the server shuts down

### Database Access
- Use `get_database()` from `app.db_processor` to get the database instance
- Use `get_jobs_collection()` to access the jobs collection
- Use `get_contacts_collection()` to access the contacts collection

## Example Usage in Routes

```python
from app.db_processor import get_jobs_collection
from app.models import JobApplication

@app.get("/api/v1/jobs")
async def list_jobs():
    collection = await get_jobs_collection()
    applications = await collection.find({}).to_list(100)
    return applications

@app.post("/api/v1/jobs")
async def create_job(job: JobApplicationCreate):
    collection = await get_jobs_collection()
    result = await collection.insert_one(job.dict(by_alias=True))
    return {"id": str(result.inserted_id)}
```

## Testing Connection

Run the server:
```bash
fastapi dev
```

If MongoDB is connected successfully, you should see:
```
🔗 Connecting to MongoDB: mongodb+srv://...
✅ Successfully connected to MongoDB database: job_tracker
```

## Troubleshooting

### Connection Error
- Verify MongoDB URI in `.env`
- Check network connectivity
- Ensure MongoDB credentials are correct
- For MongoDB Atlas, whitelist your IP address

### Database Not Initialized
- Ensure `connect_to_mongo()` is called during app startup
- Check FastAPI lifespan events are properly configured