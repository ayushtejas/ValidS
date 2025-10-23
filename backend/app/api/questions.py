from fastapi import APIRouter, HTTPException, status
from typing import List
from datetime import datetime
from bson import ObjectId

from app.models.questions import QuestionCreate, QuestionUpdate, QuestionResponse
from app.db.mongodb import get_database

router = APIRouter()


@router.post("/", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
async def create_question(question: QuestionCreate):
    """Create a new question"""
    db = get_database()

    # Validate that field exists
    if not ObjectId.is_valid(question.fields_id):
        raise HTTPException(status_code=400, detail="Invalid field ID format")

    field_exists = await db.fields.find_one({"_id": ObjectId(question.fields_id)})
    if not field_exists:
        raise HTTPException(status_code=404, detail="Field not found")

    question_dict = question.model_dump()
    question_dict["created_at"] = datetime.utcnow()
    question_dict["updated_at"] = datetime.utcnow()

    result = await db.questions.insert_one(question_dict)
    created_question = await db.questions.find_one({"_id": result.inserted_id})

    if created_question:
        created_question["_id"] = str(created_question["_id"])
        return created_question

    raise HTTPException(status_code=500, detail="Failed to create question")


@router.get("/", response_model=List[QuestionResponse])
async def get_questions(skip: int = 0, limit: int = 100):
    """Get all questions with pagination"""
    db = get_database()

    questions = []
    cursor = db.questions.find().skip(skip).limit(limit)

    async for document in cursor:
        document["_id"] = str(document["_id"])
        questions.append(document)

    return questions


@router.get("/{question_id}", response_model=QuestionResponse)
async def get_question(question_id: str):
    """Get a single question by ID"""
    if not ObjectId.is_valid(question_id):
        raise HTTPException(status_code=400, detail="Invalid question ID format")

    db = get_database()
    question = await db.questions.find_one({"_id": ObjectId(question_id)})

    if question:
        question["_id"] = str(question["_id"])
        return question

    raise HTTPException(status_code=404, detail="Question not found")


@router.get("/field/{field_id}", response_model=List[QuestionResponse])
async def get_questions_by_field(field_id: str):
    """Get all questions for a specific field"""
    if not ObjectId.is_valid(field_id):
        raise HTTPException(status_code=400, detail="Invalid field ID format")

    db = get_database()
    questions = []
    cursor = db.questions.find({"fields_id": field_id})

    async for document in cursor:
        document["_id"] = str(document["_id"])
        questions.append(document)

    return questions


@router.put("/{question_id}", response_model=QuestionResponse)
async def update_question(question_id: str, question_update: QuestionUpdate):
    """Update a question"""
    if not ObjectId.is_valid(question_id):
        raise HTTPException(status_code=400, detail="Invalid question ID format")

    db = get_database()

    # Validate field_id if provided
    if question_update.fields_id and not ObjectId.is_valid(question_update.fields_id):
        raise HTTPException(status_code=400, detail="Invalid field ID format")

    if question_update.fields_id:
        field_exists = await db.fields.find_one({"_id": ObjectId(question_update.fields_id)})
        if not field_exists:
            raise HTTPException(status_code=404, detail="Field not found")

    # Only update fields that are provided
    update_data = {k: v for k, v in question_update.model_dump(exclude_unset=True).items()}

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    update_data["updated_at"] = datetime.utcnow()

    result = await db.questions.update_one(
        {"_id": ObjectId(question_id)},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Question not found")

    updated_question = await db.questions.find_one({"_id": ObjectId(question_id)})
    if updated_question:
        updated_question["_id"] = str(updated_question["_id"])
        return updated_question

    raise HTTPException(status_code=500, detail="Failed to retrieve updated question")


@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(question_id: str):
    """Delete a question"""
    if not ObjectId.is_valid(question_id):
        raise HTTPException(status_code=400, detail="Invalid question ID format")

    db = get_database()
    result = await db.questions.delete_one({"_id": ObjectId(question_id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Question not found")

    return None
