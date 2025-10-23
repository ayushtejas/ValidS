from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

from app.models.user import UserRole
from app.models.questions import QuestionResponse
from app.models.controls import ControlResponse
from app.core.auth import get_current_user, require_auditor, require_spectator
from app.db.mongodb import get_database

router = APIRouter()


@router.get("/questions/role-based", response_model=List[QuestionResponse])
async def get_role_based_questions(
    user_id: str = Query(..., description="User ID to get questions for"),
    iso_id: Optional[str] = Query(None, description="Filter by ISO standard"),
    current_user: dict = Depends(get_current_user)
):
    """Get questions assigned to a specific user based on their role and experience"""
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    db = get_database()

    # Get user details
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if current user has access to this user's company
    if not check_company_access(current_user, user.get("company_id")):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this user's data"
        )

    # Build filter for questions based on user role and experience
    filter_dict = {"is_active": True}

    # Get questions based on user role and experience
    user_role = user.get("roletype")
    experience_years = user.get("experience_years", 0)

    # This is where you'd implement your business logic for question assignment
    # For now, we'll get all active questions and let the frontend filter
    questions = []
    cursor = db.questions.find(filter_dict)

    async for document in cursor:
        document["_id"] = str(document["_id"])
        questions.append(document)

    return questions


@router.get("/controls/company/{company_id}", response_model=List[ControlResponse])
async def get_company_controls(
    company_id: str,
    current_user: dict = Depends(require_auditor)
):
    """Get controls available for a specific company"""
    if not ObjectId.is_valid(company_id):
        raise HTTPException(status_code=400, detail="Invalid company ID format")

    # Check if user has access to this company
    if not check_company_access(current_user, company_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this company"
        )

    db = get_database()

    # Get company details
    company = await db.companies.find_one({"_id": ObjectId(company_id)})
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Get ISO standards for this company
    iso_standards = []
    cursor = db.iso.find({"is_active": True})
    async for iso in cursor:
        iso_standards.append(iso)

    # Get controls for the ISO standards
    controls = []
    for iso in iso_standards:
        control_cursor = db.controls.find({
            "is_active": True,
            "_id": ObjectId(iso.get("control_id"))
        })
        async for control in control_cursor:
            control["_id"] = str(control["_id"])
            controls.append(control)

    return controls


@router.get("/users/company/{company_id}")
async def get_company_users(
    company_id: str,
    current_user: dict = Depends(require_auditor)
):
    """Get all users in a company for assignment purposes"""
    if not ObjectId.is_valid(company_id):
        raise HTTPException(status_code=400, detail="Invalid company ID format")

    # Check if user has access to this company
    if not check_company_access(current_user, company_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this company"
        )

    db = get_database()

    users = []
    cursor = db.users.find({
        "company_id": company_id,
        "is_active": True
    })

    async for document in cursor:
        document["_id"] = str(document["_id"])
        # Remove password from response
        if "password" in document:
            del document["password"]
        users.append(document)

    return users


@router.post("/questions/assign")
async def assign_questions_to_user(
    user_id: str,
    question_ids: List[str],
    current_user: dict = Depends(require_auditor)
):
    """Assign specific questions to a user"""
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    # Validate all question IDs
    for question_id in question_ids:
        if not ObjectId.is_valid(question_id):
            raise HTTPException(status_code=400, detail=f"Invalid question ID: {question_id}")

    db = get_database()

    # Get user details
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if user has access to this user's company
    if not check_company_access(current_user, user.get("company_id")):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this user's data"
        )

    # Validate that all questions exist
    for question_id in question_ids:
        question = await db.questions.find_one({"_id": ObjectId(question_id)})
        if not question:
            raise HTTPException(status_code=404, detail=f"Question not found: {question_id}")

    # Create assignment record (you might want to create a separate assignments collection)
    assignment = {
        "user_id": user_id,
        "question_ids": question_ids,
        "assigned_by": current_user["_id"],
        "assigned_at": datetime.utcnow(),
        "is_active": True
    }

    result = await db.question_assignments.insert_one(assignment)

    return {
        "message": "Questions assigned successfully",
        "assignment_id": str(result.inserted_id),
        "assigned_questions": len(question_ids)
    }


def check_company_access(user: dict, company_id: str) -> bool:
    """Check if user has access to a specific company"""
    user_role = user.get("roletype")
    user_company_id = user.get("company_id")

    # Superadmin has access to all companies
    if user_role == "superadmin":
        return True

    # Other users can only access their own company
    return user_company_id == company_id
