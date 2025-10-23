from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

from app.models.submissions import (
    SubmissionCreate, SubmissionUpdate, SubmissionResponse,
    SubmissionProgress, SubmissionStatus
)
from app.core.auth import get_current_user, require_employee, check_company_access
from app.db.mongodb import get_database

router = APIRouter()


@router.post("/", response_model=SubmissionResponse, status_code=status.HTTP_201_CREATED)
async def create_submission(
    submission: SubmissionCreate,
    current_user: dict = Depends(require_employee)
):
    """Create a new compliance form submission"""
    db = get_database()

    # Validate company access
    if not check_company_access(current_user, submission.company_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this company"
        )

    # Validate that user, company, and ISO exist
    if not ObjectId.is_valid(submission.user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    if not ObjectId.is_valid(submission.company_id):
        raise HTTPException(status_code=400, detail="Invalid company ID format")

    if not ObjectId.is_valid(submission.iso_id):
        raise HTTPException(status_code=400, detail="Invalid ISO ID format")

    # Check if user exists and belongs to the company
    user = await db.users.find_one({"_id": ObjectId(submission.user_id)})
    if not user or user.get("company_id") != submission.company_id:
        raise HTTPException(status_code=404, detail="User not found or doesn't belong to this company")

    # Check if company exists
    company = await db.companies.find_one({"_id": ObjectId(submission.company_id)})
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Check if ISO exists
    iso = await db.iso.find_one({"_id": ObjectId(submission.iso_id)})
    if not iso:
        raise HTTPException(status_code=404, detail="ISO standard not found")

    submission_dict = submission.model_dump()
    submission_dict["created_at"] = datetime.utcnow()
    submission_dict["updated_at"] = datetime.utcnow()

    result = await db.submissions.insert_one(submission_dict)
    created_submission = await db.submissions.find_one({"_id": result.inserted_id})

    if created_submission:
        created_submission["_id"] = str(created_submission["_id"])
        return created_submission

    raise HTTPException(status_code=500, detail="Failed to create submission")


@router.get("/", response_model=List[SubmissionResponse])
async def get_submissions(
    company_id: Optional[str] = Query(None, description="Filter by company ID"),
    status: Optional[SubmissionStatus] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(get_current_user)
):
    """Get submissions with filtering"""
    db = get_database()

    # Build filter based on user role and permissions
    filter_dict = {}

    if current_user.get("roletype") == "superadmin":
        # Superadmin can see all submissions
        if company_id:
            filter_dict["company_id"] = company_id
    elif current_user.get("roletype") in ["auditor", "spectator"]:
        # Auditor and spectator can only see their company's submissions
        user_company_id = current_user.get("company_id")
        if not user_company_id:
            raise HTTPException(
                status_code=403,
                detail="User not associated with any company"
            )
        filter_dict["company_id"] = user_company_id
    else:
        # Employees can only see their own submissions
        filter_dict["user_id"] = current_user["_id"]

    if status:
        filter_dict["status"] = status.value

    submissions = []
    cursor = db.submissions.find(filter_dict).skip(skip).limit(limit)

    async for document in cursor:
        document["_id"] = str(document["_id"])
        submissions.append(document)

    return submissions


@router.get("/{submission_id}", response_model=SubmissionResponse)
async def get_submission(
    submission_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a single submission by ID"""
    if not ObjectId.is_valid(submission_id):
        raise HTTPException(status_code=400, detail="Invalid submission ID format")

    db = get_database()
    submission = await db.submissions.find_one({"_id": ObjectId(submission_id)})

    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    # Check access permissions
    if not check_company_access(current_user, submission["company_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this submission"
        )

    submission["_id"] = str(submission["_id"])
    return submission


@router.get("/company/{company_id}/progress", response_model=List[SubmissionProgress])
async def get_company_progress(
    company_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get progress overview for a company (spectator view)"""
    if not ObjectId.is_valid(company_id):
        raise HTTPException(status_code=400, detail="Invalid company ID format")

    # Check if user has access to this company
    if not check_company_access(current_user, company_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this company"
        )

    db = get_database()

    # Get all submissions for the company
    submissions = []
    cursor = db.submissions.find({"company_id": company_id})

    async for submission in cursor:
        # Get user details
        user = await db.users.find_one({"_id": ObjectId(submission["user_id"])})
        if user:
            progress = SubmissionProgress(
                total_questions=len(submission.get("submission_data", {})),
                completed_questions=len([v for v in submission.get("submission_data", {}).values() if v]),
                progress_percentage=submission.get("progress_percentage", 0),
                status=SubmissionStatus(submission.get("status", "draft")),
                last_updated=submission.get("updated_at", submission.get("created_at")),
                user_name=user.get("username", "Unknown"),
                user_role=user.get("roletype", "employee")
            )
            submissions.append(progress)

    return submissions


@router.put("/{submission_id}", response_model=SubmissionResponse)
async def update_submission(
    submission_id: str,
    submission_update: SubmissionUpdate,
    current_user: dict = Depends(require_employee)
):
    """Update a submission"""
    if not ObjectId.is_valid(submission_id):
        raise HTTPException(status_code=400, detail="Invalid submission ID format")

    db = get_database()

    # Get existing submission
    existing_submission = await db.submissions.find_one({"_id": ObjectId(submission_id)})
    if not existing_submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    # Check access permissions
    if not check_company_access(current_user, existing_submission["company_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this submission"
        )

    # Only update fields that are provided
    update_data = {k: v for k, v in submission_update.model_dump(exclude_unset=True).items()}

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    # Set timestamps based on status changes
    if "status" in update_data:
        if update_data["status"] == "submitted" and existing_submission.get("status") == "draft":
            update_data["submitted_at"] = datetime.utcnow()
        elif update_data["status"] in ["approved", "rejected", "requires_changes"]:
            update_data["reviewed_at"] = datetime.utcnow()

    update_data["updated_at"] = datetime.utcnow()

    result = await db.submissions.update_one(
        {"_id": ObjectId(submission_id)},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Submission not found")

    updated_submission = await db.submissions.find_one({"_id": ObjectId(submission_id)})
    if updated_submission:
        updated_submission["_id"] = str(updated_submission["_id"])
        return updated_submission

    raise HTTPException(status_code=500, detail="Failed to retrieve updated submission")


@router.delete("/{submission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_submission(
    submission_id: str,
    current_user: dict = Depends(require_employee)
):
    """Delete a submission"""
    if not ObjectId.is_valid(submission_id):
        raise HTTPException(status_code=400, detail="Invalid submission ID format")

    db = get_database()

    # Get existing submission to check permissions
    existing_submission = await db.submissions.find_one({"_id": ObjectId(submission_id)})
    if not existing_submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    # Check access permissions
    if not check_company_access(current_user, existing_submission["company_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this submission"
        )

    result = await db.submissions.delete_one({"_id": ObjectId(submission_id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Submission not found")

    return None
