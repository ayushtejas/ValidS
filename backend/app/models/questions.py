from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId


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


class QuestionBase(BaseModel):
    description: str = Field(..., min_length=1, max_length=2000)
    is_active: bool = True


class QuestionCreate(QuestionBase):
    fields_id: str = Field(..., description="Field ID associated with this question")


class QuestionUpdate(BaseModel):
    description: Optional[str] = Field(None, min_length=1, max_length=2000)
    fields_id: Optional[str] = None
    is_active: Optional[bool] = None


class QuestionInDB(QuestionBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    fields_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class QuestionResponse(QuestionBase):
    id: str = Field(alias="_id")
    fields_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "description": "What security measures are in place for data access?",
                "fields_id": "507f1f77bcf86cd799439012",
                "is_active": True,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
            }
        }
