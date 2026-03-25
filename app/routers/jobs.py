from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.models import JobApplication, JobApplicationCreate, JobApplicationUpdate
from app.db_operations import create_job, get_jobs, get_job_by_id, update_job, delete_job, get_stats
from app.routers.auth import verify_token
from app.db_processor import get_db

router = APIRouter()


@router.get("/jobs", response_model=List[dict])
async def list_jobs(skip: int = 0, limit: int = 100, userid: str = Depends(verify_token), db = Depends(get_db)):
    """Get all job applications"""
    try:
        jobs = await get_jobs(db, skip=skip, limit=limit)
        return jobs
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/jobs", response_model=dict)
async def create_new_job(job: JobApplicationCreate, userid: str = Depends(verify_token), db = Depends(get_db)):
    """Create a new job application"""
    try:
        result = await create_job(job, db)
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/jobs/{job_id}", response_model=dict)
async def get_job(job_id: str, userid: str = Depends(verify_token), db = Depends(get_db)):
    """Get a specific job application by ID"""
    try:
        job = await get_job_by_id(job_id, db)
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
        return job
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/jobs/{job_id}", response_model=dict)
async def update_job_app(job_id: str, job: JobApplicationUpdate, userid: str = Depends(verify_token), db = Depends(get_db)):
    """Update a job application"""
    try:
        result = await update_job(job_id, job, db)
        if "error" in result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/jobs/{job_id}", response_model=dict)
async def delete_job_app(job_id: str, userid: str = Depends(verify_token), db = Depends(get_db)):
    """Delete a job application"""
    try:
        result = await delete_job(job_id, db)
        if "error" in result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/stats")
async def get_job_stats(userid: str = Depends(verify_token), db = Depends(get_db)):
    """Get statistics about job applications"""
    try:
        stats = await get_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))