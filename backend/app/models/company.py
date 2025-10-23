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


class CompanyBase(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=200)
    company_description: Optional[str] = Field(None, max_length=1000)
    is_active: bool = True


class CompanyCreate(CompanyBase):
    user_id: str = Field(..., description="User ID who owns this company")
    iso_id: str = Field(..., description="ISO standard ID")


class CompanyUpdate(BaseModel):
    company_name: Optional[str] = Field(None, min_length=1, max_length=200)
    company_description: Optional[str] = Field(None, max_length=1000)
    user_id: Optional[str] = None
    iso_id: Optional[str] = None
    is_active: Optional[bool] = None


class CompanyInDB(CompanyBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    iso_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class CompanyResponse(CompanyBase):
    id: str = Field(alias="_id")
    user_id: str
    iso_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "company_name": "Acme Corporation",
                "company_description": "A leading technology company",
                "user_id": "507f1f77bcf86cd799439012",
                "iso_id": "507f1f77bcf86cd799439013",
                "is_active": True,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
            }
        }
