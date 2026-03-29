"""
Pydantic models for Job Tracker database schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError(f"Invalid ObjectId: {v}")
        return ObjectId(v)

    def __repr__(self):
        return f"ObjectId('{self}')"


class User(BaseModel):
    """User model"""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    userid: str
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True


class UserCreate(BaseModel):
    """Request model for creating user"""
    userid: str
    password: str


class UserLogin(BaseModel):
    """Request model for user login"""
    userid: str
    password: str


class Token(BaseModel):
    """Token response model"""
    access_token: str
    token_type: str = "bearer"


class LinkedInContact(BaseModel):
    """LinkedI Contact model"""
    name: str
    dept: Optional[str] = None
    role: Optional[str] = None
    status: str = "not-sent"  # not-sent, requested, connected

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "dept": "Engineering",
                "role": "Senior Engineer",
                "status": "connected"
            }
        }


class JobApplication(BaseModel):
    """Job Application model"""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    company: str
    role: str
    platform: Optional[str] = "LinkedIn"
    status: str = "applied"  # applied, screening, interview, technical, offer, rejected, ghosted
    date: Optional[str] = None
    url: Optional[str] = None
    notes: Optional[str] = None
    contacts: List[LinkedInContact] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_schema_extra = {
            "example": {
                "company": "Razorpay",
                "role": "Backend Engineer",
                "platform": "LinkedIn",
                "status": "interview",
                "date": "2024-03-24",
                "url": "https://example.com/job",
                "notes": "Second round scheduled for March 30",
                "contacts": [
                    {
                        "name": "Priya Sharma",
                        "dept": "Engineering",
                        "status": "connected"
                    }
                ]
            }
        }


class JobApplicationCreate(BaseModel):
    """Request model for creating job application"""
    company: str
    role: str
    user_id: str
    platform: Optional[str] = "LinkedIn"
    status: Optional[str] = "applied"
    date: Optional[str] = None
    url: Optional[str] = None
    notes: Optional[str] = None
    contacts: Optional[List[LinkedInContact]] = []


class JobApplicationUpdate(BaseModel):
    """Request model for updating job application"""
    company: Optional[str] = None
    role: Optional[str] = None
    platform: Optional[str] = None
    status: Optional[str] = None
    date: Optional[str] = None
    url: Optional[str] = None
    notes: Optional[str] = None
    contacts: Optional[List[LinkedInContact]] = None