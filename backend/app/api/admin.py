from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from datetime import datetime
from bson import ObjectId
import hashlib

from app.models.user import UserCreate, UserResponse, UserRole
from app.core.auth import get_current_user
from app.db.mongodb import get_database

router = APIRouter()


def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


@router.post("/create-superadmin", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_superadmin(
    username: str,
    email: str,
    password: str
):
    """Create a superadmin user (no authentication required for initial setup)"""
    db = get_database()

    # Check if superadmin already exists
    existing_superadmin = await db.users.find_one({"roletype": "superadmin"})
    if existing_superadmin:
        raise HTTPException(
            status_code=400,
            detail="Superadmin already exists in the system"
        )

    # Validate input
    if len(username) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters")

    if len(password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    # Check if username or email already exists
    existing_user = await db.users.find_one({
        "$or": [
            {"username": username},
            {"email": email}
        ]
    })

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username or email already exists"
        )

    # Create superadmin
    superadmin_data = {
        "username": username,
        "roletype": "superadmin",
        "email": email,
        "password": hash_password(password),
        "company_id": None,
        "experience_years": None,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    result = await db.users.insert_one(superadmin_data)
    created_user = await db.users.find_one({"_id": result.inserted_id})

    if created_user:
        created_user["_id"] = str(created_user["_id"])
        # Remove password from response
        del created_user["password"]
        return created_user

    raise HTTPException(status_code=500, detail="Failed to create superadmin")


@router.get("/system-status")
async def get_system_status():
    """Get system status and user counts"""
    db = get_database()

    # Count users by role
    user_counts = {}
    for role in ["superadmin", "auditor", "spectator", "employee"]:
        count = await db.users.count_documents({"roletype": role, "is_active": True})
        user_counts[role] = count

    # Count companies
    company_count = await db.companies.count_documents({"is_active": True})

    # Count ISO standards
    iso_count = await db.iso.count_documents({"is_active": True})

    # Count submissions
    submission_count = await db.submissions.count_documents({})

    return {
        "system_status": "operational",
        "user_counts": user_counts,
        "company_count": company_count,
        "iso_count": iso_count,
        "submission_count": submission_count,
        "total_users": sum(user_counts.values())
    }


@router.get("/users/role/{role}", response_model=List[UserResponse])
async def get_users_by_role(
    role: str,
    current_user: dict = Depends(get_current_user)
):
    """Get users by role (superadmin only)"""
    if current_user.get("roletype") != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superadmin can access this endpoint"
        )

    if role not in ["superadmin", "auditor", "spectator", "employee"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid role. Must be one of: superadmin, auditor, spectator, employee"
        )

    db = get_database()
    users = []
    cursor = db.users.find({"roletype": role, "is_active": True})

    async for document in cursor:
        document["_id"] = str(document["_id"])
        # Remove password from response
        if "password" in document:
            del document["password"]
        users.append(document)

    return users


@router.post("/reset-password/{user_id}")
async def reset_user_password(
    user_id: str,
    new_password: str,
    current_user: dict = Depends(get_current_user)
):
    """Reset user password (superadmin only)"""
    if current_user.get("roletype") != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superadmin can reset passwords"
        )

    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    if len(new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    db = get_database()

    # Update user password
    result = await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {
            "$set": {
                "password": hash_password(new_password),
                "updated_at": datetime.utcnow()
            }
        }
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": "Password reset successfully"}


@router.post("/deactivate-user/{user_id}")
async def deactivate_user(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Deactivate a user (superadmin only)"""
    if current_user.get("roletype") != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superadmin can deactivate users"
        )

    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    # Prevent deactivating self
    if current_user["_id"] == user_id:
        raise HTTPException(
            status_code=400,
            detail="Cannot deactivate your own account"
        )

    db = get_database()

    # Deactivate user
    result = await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {
            "$set": {
                "is_active": False,
                "updated_at": datetime.utcnow()
            }
        }
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": "User deactivated successfully"}
