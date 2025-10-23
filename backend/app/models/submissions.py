from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from bson import ObjectId
from enum import Enum


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")


class SubmissionStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_CHANGES = "requires_changes"


class SubmissionBase(BaseModel):
    user_id: str = Field(..., description="User who submitted the form")
    company_id: str = Field(..., description="Company the submission belongs to")
    iso_id: str = Field(..., description="ISO standard being assessed")
    status: SubmissionStatus = SubmissionStatus.DRAFT
    submission_data: Dict[str, Any] = Field(..., description="Form submission data")
    reviewer_notes: Optional[str] = Field(None, max_length=2000)
    progress_percentage: int = Field(0, ge=0, le=100, description="Completion percentage")


class SubmissionCreate(SubmissionBase):
    pass


class SubmissionUpdate(BaseModel):
    status: Optional[SubmissionStatus] = None
    submission_data: Optional[Dict[str, Any]] = None
    reviewer_notes: Optional[str] = Field(None, max_length=2000)
    progress_percentage: Optional[int] = Field(None, ge=0, le=100)


class SubmissionInDB(SubmissionBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    submitted_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class SubmissionResponse(SubmissionBase):
    id: str = Field(alias="_id")
    created_at: datetime
    updated_at: datetime
    submitted_at: Optional[datetime]
    reviewed_at: Optional[datetime]

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "user_id": "507f1f77bcf86cd799439012",
                "company_id": "507f1f77bcf86cd799439013",
                "iso_id": "507f1f77bcf86cd799439014",
                "status": "draft",
                "submission_data": {"question_1": "answer_1", "question_2": "answer_2"},
                "progress_percentage": 75,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        }


class SubmissionProgress(BaseModel):
    """Progress tracking for spectators"""
    total_questions: int
    completed_questions: int
    progress_percentage: int
    status: SubmissionStatus
    last_updated: datetime
    user_name: str
    user_role: str
