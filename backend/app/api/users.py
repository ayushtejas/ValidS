from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from datetime import datetime
from bson import ObjectId
import hashlib

from app.models.user import UserCreate, UserUpdate, UserResponse
from app.db.mongodb import get_database

router = APIRouter()


def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    """Create a new user"""
    db = get_database()

    # Check if username or email already exists
    existing_user = await db.users.find_one({
        "$or": [
            {"username": user.username},
            {"email": user.email}
        ]
    })

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username or email already exists"
        )

    user_dict = user.model_dump()
    user_dict["password"] = hash_password(user_dict["password"])
    user_dict["created_at"] = datetime.utcnow()
    user_dict["updated_at"] = datetime.utcnow()

    result = await db.users.insert_one(user_dict)
    created_user = await db.users.find_one({"_id": result.inserted_id})

    if created_user:
        created_user["_id"] = str(created_user["_id"])
        # Remove password from response
        del created_user["password"]
        return created_user

    raise HTTPException(status_code=500, detail="Failed to create user")


@router.get("/", response_model=List[UserResponse])
async def get_users(skip: int = 0, limit: int = 100):
    """Get all users with pagination"""
    db = get_database()

    users = []
    cursor = db.users.find().skip(skip).limit(limit)

    async for document in cursor:
        document["_id"] = str(document["_id"])
        # Remove password from response
        del document["password"]
        users.append(document)

    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """Get a single user by ID"""
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    db = get_database()
    user = await db.users.find_one({"_id": ObjectId(user_id)})

    if user:
        user["_id"] = str(user["_id"])
        # Remove password from response
        del user["password"]
        return user

    raise HTTPException(status_code=404, detail="User not found")


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, user_update: UserUpdate):
    """Update a user"""
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    db = get_database()

    # Only update fields that are provided
    update_data = {k: v for k, v in user_update.model_dump(exclude_unset=True).items()}

    # Hash password if provided
    if "password" in update_data:
        update_data["password"] = hash_password(update_data["password"])

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    update_data["updated_at"] = datetime.utcnow()

    result = await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    updated_user = await db.users.find_one({"_id": ObjectId(user_id)})
    if updated_user:
        updated_user["_id"] = str(updated_user["_id"])
        # Remove password from response
        del updated_user["password"]
        return updated_user

    raise HTTPException(status_code=500, detail="Failed to retrieve updated user")


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str):
    """Delete a user"""
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    db = get_database()
    result = await db.users.delete_one({"_id": ObjectId(user_id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return None
