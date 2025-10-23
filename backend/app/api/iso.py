from fastapi import APIRouter, HTTPException, status
from typing import List
from datetime import datetime
from bson import ObjectId

from app.models.iso import ISOCreate, ISOUpdate, ISOResponse
from app.db.mongodb import get_database

router = APIRouter()


@router.post("/", response_model=ISOResponse, status_code=status.HTTP_201_CREATED)
async def create_iso(iso: ISOCreate):
    """Create a new ISO standard"""
    db = get_database()

    # Validate that control exists
    if not ObjectId.is_valid(iso.control_id):
        raise HTTPException(status_code=400, detail="Invalid control ID format")

    control_exists = await db.controls.find_one({"_id": ObjectId(iso.control_id)})
    if not control_exists:
        raise HTTPException(status_code=404, detail="Control not found")

    iso_dict = iso.model_dump()
    iso_dict["created_at"] = datetime.utcnow()
    iso_dict["updated_at"] = datetime.utcnow()

    result = await db.iso.insert_one(iso_dict)
    created_iso = await db.iso.find_one({"_id": result.inserted_id})

    if created_iso:
        created_iso["_id"] = str(created_iso["_id"])
        return created_iso

    raise HTTPException(status_code=500, detail="Failed to create ISO")


@router.get("/", response_model=List[ISOResponse])
async def get_iso_standards(skip: int = 0, limit: int = 100):
    """Get all ISO standards with pagination"""
    db = get_database()

    iso_standards = []
    cursor = db.iso.find().skip(skip).limit(limit)

    async for document in cursor:
        document["_id"] = str(document["_id"])
        iso_standards.append(document)

    return iso_standards


@router.get("/{iso_id}", response_model=ISOResponse)
async def get_iso(iso_id: str):
    """Get a single ISO standard by ID"""
    if not ObjectId.is_valid(iso_id):
        raise HTTPException(status_code=400, detail="Invalid ISO ID format")

    db = get_database()
    iso = await db.iso.find_one({"_id": ObjectId(iso_id)})

    if iso:
        iso["_id"] = str(iso["_id"])
        return iso

    raise HTTPException(status_code=404, detail="ISO not found")


@router.get("/control/{control_id}", response_model=List[ISOResponse])
async def get_iso_by_control(control_id: str):
    """Get all ISO standards for a specific control"""
    if not ObjectId.is_valid(control_id):
        raise HTTPException(status_code=400, detail="Invalid control ID format")

    db = get_database()
    iso_standards = []
    cursor = db.iso.find({"control_id": control_id})

    async for document in cursor:
        document["_id"] = str(document["_id"])
        iso_standards.append(document)

    return iso_standards


@router.put("/{iso_id}", response_model=ISOResponse)
async def update_iso(iso_id: str, iso_update: ISOUpdate):
    """Update an ISO standard"""
    if not ObjectId.is_valid(iso_id):
        raise HTTPException(status_code=400, detail="Invalid ISO ID format")

    db = get_database()

    # Validate control_id if provided
    if iso_update.control_id and not ObjectId.is_valid(iso_update.control_id):
        raise HTTPException(status_code=400, detail="Invalid control ID format")

    if iso_update.control_id:
        control_exists = await db.controls.find_one({"_id": ObjectId(iso_update.control_id)})
        if not control_exists:
            raise HTTPException(status_code=404, detail="Control not found")

    # Only update fields that are provided
    update_data = {k: v for k, v in iso_update.model_dump(exclude_unset=True).items()}

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    update_data["updated_at"] = datetime.utcnow()

    result = await db.iso.update_one(
        {"_id": ObjectId(iso_id)},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="ISO not found")

    updated_iso = await db.iso.find_one({"_id": ObjectId(iso_id)})
    if updated_iso:
        updated_iso["_id"] = str(updated_iso["_id"])
        return updated_iso

    raise HTTPException(status_code=500, detail="Failed to retrieve updated ISO")


@router.delete("/{iso_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_iso(iso_id: str):
    """Delete an ISO standard"""
    if not ObjectId.is_valid(iso_id):
        raise HTTPException(status_code=400, detail="Invalid ISO ID format")

    db = get_database()
    result = await db.iso.delete_one({"_id": ObjectId(iso_id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="ISO not found")

    return None
