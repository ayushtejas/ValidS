from pydantic import BaseModel, Field
from typing import Optional, List
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


class FieldBase(BaseModel):
    field_name: str = Field(..., min_length=1, max_length=200)
    fieldType: str = Field(..., max_length=50)  # text, number, boolean, select, etc.
    isRequired: bool = False
    options: Optional[List[str]] = Field(None, description="Options for select/radio fields")
    is_active: bool = True


class FieldCreate(FieldBase):
    pass


class FieldUpdate(BaseModel):
    field_name: Optional[str] = Field(None, min_length=1, max_length=200)
    fieldType: Optional[str] = Field(None, max_length=50)
    isRequired: Optional[bool] = None
    options: Optional[List[str]] = None
    is_active: Optional[bool] = None


class FieldInDB(FieldBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class FieldResponse(FieldBase):
    id: str = Field(alias="_id")
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "field_name": "Security Level",
                "fieldType": "select",
                "isRequired": True,
                "options": ["Low", "Medium", "High", "Critical"],
                "is_active": True,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
            }
        }
