from fastapi import APIRouter, HTTPException, status
from typing import List
from datetime import datetime
from bson import ObjectId

from app.models.fields import FieldCreate, FieldUpdate, FieldResponse
from app.db.mongodb import get_database

router = APIRouter()


@router.post("/", response_model=FieldResponse, status_code=status.HTTP_201_CREATED)
async def create_field(field: FieldCreate):
    """Create a new field"""
    db = get_database()

    field_dict = field.model_dump()
    field_dict["created_at"] = datetime.utcnow()
    field_dict["updated_at"] = datetime.utcnow()

    result = await db.fields.insert_one(field_dict)
    created_field = await db.fields.find_one({"_id": result.inserted_id})

    if created_field:
        created_field["_id"] = str(created_field["_id"])
        return created_field

    raise HTTPException(status_code=500, detail="Failed to create field")


@router.get("/", response_model=List[FieldResponse])
async def get_fields(skip: int = 0, limit: int = 100):
    """Get all fields with pagination"""
    db = get_database()

    fields = []
    cursor = db.fields.find().skip(skip).limit(limit)

    async for document in cursor:
        document["_id"] = str(document["_id"])
        fields.append(document)

    return fields


@router.get("/{field_id}", response_model=FieldResponse)
async def get_field(field_id: str):
    """Get a single field by ID"""
    if not ObjectId.is_valid(field_id):
        raise HTTPException(status_code=400, detail="Invalid field ID format")

    db = get_database()
    field = await db.fields.find_one({"_id": ObjectId(field_id)})

    if field:
        field["_id"] = str(field["_id"])
        return field

    raise HTTPException(status_code=404, detail="Field not found")


@router.get("/type/{field_type}", response_model=List[FieldResponse])
async def get_fields_by_type(field_type: str):
    """Get all fields of a specific type"""
    db = get_database()
    fields = []
    cursor = db.fields.find({"fieldType": field_type})

    async for document in cursor:
        document["_id"] = str(document["_id"])
        fields.append(document)

    return fields


@router.put("/{field_id}", response_model=FieldResponse)
async def update_field(field_id: str, field_update: FieldUpdate):
    """Update a field"""
    if not ObjectId.is_valid(field_id):
        raise HTTPException(status_code=400, detail="Invalid field ID format")

    db = get_database()

    # Only update fields that are provided
    update_data = {k: v for k, v in field_update.model_dump(exclude_unset=True).items()}

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    update_data["updated_at"] = datetime.utcnow()

    result = await db.fields.update_one(
        {"_id": ObjectId(field_id)},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Field not found")

    updated_field = await db.fields.find_one({"_id": ObjectId(field_id)})
    if updated_field:
        updated_field["_id"] = str(updated_field["_id"])
        return updated_field

    raise HTTPException(status_code=500, detail="Failed to retrieve updated field")


@router.delete("/{field_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_field(field_id: str):
    """Delete a field"""
    if not ObjectId.is_valid(field_id):
        raise HTTPException(status_code=400, detail="Invalid field ID format")

    db = get_database()
    result = await db.fields.delete_one({"_id": ObjectId(field_id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Field not found")

    return None
