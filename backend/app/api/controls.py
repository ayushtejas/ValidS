from fastapi import APIRouter, HTTPException, status
from typing import List
from datetime import datetime
from bson import ObjectId

from app.models.controls import ControlCreate, ControlUpdate, ControlResponse
from app.db.mongodb import get_database

router = APIRouter()


@router.post("/", response_model=ControlResponse, status_code=status.HTTP_201_CREATED)
async def create_control(control: ControlCreate):
    """Create a new control"""
    db = get_database()

    # Validate that question exists
    if not ObjectId.is_valid(control.question_id):
        raise HTTPException(status_code=400, detail="Invalid question ID format")

    question_exists = await db.questions.find_one({"_id": ObjectId(control.question_id)})
    if not question_exists:
        raise HTTPException(status_code=404, detail="Question not found")

    control_dict = control.model_dump()
    control_dict["created_at"] = datetime.utcnow()
    control_dict["updated_at"] = datetime.utcnow()

    result = await db.controls.insert_one(control_dict)
    created_control = await db.controls.find_one({"_id": result.inserted_id})

    if created_control:
        created_control["_id"] = str(created_control["_id"])
        return created_control

    raise HTTPException(status_code=500, detail="Failed to create control")


@router.get("/", response_model=List[ControlResponse])
async def get_controls(skip: int = 0, limit: int = 100):
    """Get all controls with pagination"""
    db = get_database()

    controls = []
    cursor = db.controls.find().skip(skip).limit(limit)

    async for document in cursor:
        document["_id"] = str(document["_id"])
        controls.append(document)

    return controls


@router.get("/{control_id}", response_model=ControlResponse)
async def get_control(control_id: str):
    """Get a single control by ID"""
    if not ObjectId.is_valid(control_id):
        raise HTTPException(status_code=400, detail="Invalid control ID format")

    db = get_database()
    control = await db.controls.find_one({"_id": ObjectId(control_id)})

    if control:
        control["_id"] = str(control["_id"])
        return control

    raise HTTPException(status_code=404, detail="Control not found")


@router.get("/question/{question_id}", response_model=List[ControlResponse])
async def get_controls_by_question(question_id: str):
    """Get all controls for a specific question"""
    if not ObjectId.is_valid(question_id):
        raise HTTPException(status_code=400, detail="Invalid question ID format")

    db = get_database()
    controls = []
    cursor = db.controls.find({"question_id": question_id})

    async for document in cursor:
        document["_id"] = str(document["_id"])
        controls.append(document)

    return controls


@router.put("/{control_id}", response_model=ControlResponse)
async def update_control(control_id: str, control_update: ControlUpdate):
    """Update a control"""
    if not ObjectId.is_valid(control_id):
        raise HTTPException(status_code=400, detail="Invalid control ID format")

    db = get_database()

    # Validate question_id if provided
    if control_update.question_id and not ObjectId.is_valid(control_update.question_id):
        raise HTTPException(status_code=400, detail="Invalid question ID format")

    if control_update.question_id:
        question_exists = await db.questions.find_one({"_id": ObjectId(control_update.question_id)})
        if not question_exists:
            raise HTTPException(status_code=404, detail="Question not found")

    # Only update fields that are provided
    update_data = {k: v for k, v in control_update.model_dump(exclude_unset=True).items()}

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    update_data["updated_at"] = datetime.utcnow()

    result = await db.controls.update_one(
        {"_id": ObjectId(control_id)},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Control not found")

    updated_control = await db.controls.find_one({"_id": ObjectId(control_id)})
    if updated_control:
        updated_control["_id"] = str(updated_control["_id"])
        return updated_control

    raise HTTPException(status_code=500, detail="Failed to retrieve updated control")


@router.delete("/{control_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_control(control_id: str):
    """Delete a control"""
    if not ObjectId.is_valid(control_id):
        raise HTTPException(status_code=400, detail="Invalid control ID format")

    db = get_database()
    result = await db.controls.delete_one({"_id": ObjectId(control_id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Control not found")

    return None
