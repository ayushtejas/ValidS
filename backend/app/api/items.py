from fastapi import APIRouter, HTTPException, status
from typing import List
from datetime import datetime
from bson import ObjectId

from app.models.item import ItemCreate, ItemUpdate, ItemResponse
from app.db.mongodb import get_database

router = APIRouter()


@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemCreate):
    """Create a new item"""
    db = get_database()

    item_dict = item.model_dump()
    item_dict["created_at"] = datetime.utcnow()
    item_dict["updated_at"] = datetime.utcnow()

    result = await db.items.insert_one(item_dict)
    created_item = await db.items.find_one({"_id": result.inserted_id})

    if created_item:
        created_item["_id"] = str(created_item["_id"])
        return created_item

    raise HTTPException(status_code=500, detail="Failed to create item")


@router.get("/", response_model=List[ItemResponse])
async def get_items(skip: int = 0, limit: int = 100):
    """Get all items with pagination"""
    db = get_database()

    items = []
    cursor = db.items.find().skip(skip).limit(limit)

    async for document in cursor:
        document["_id"] = str(document["_id"])
        items.append(document)

    return items


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: str):
    """Get a single item by ID"""
    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=400, detail="Invalid item ID format")

    db = get_database()
    item = await db.items.find_one({"_id": ObjectId(item_id)})

    if item:
        item["_id"] = str(item["_id"])
        return item

    raise HTTPException(status_code=404, detail="Item not found")


@router.put("/{item_id}", response_model=ItemResponse)
async def update_item(item_id: str, item_update: ItemUpdate):
    """Update an item"""
    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=400, detail="Invalid item ID format")

    db = get_database()

    # Only update fields that are provided
    update_data = {k: v for k, v in item_update.model_dump(exclude_unset=True).items()}

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    update_data["updated_at"] = datetime.utcnow()

    result = await db.items.update_one(
        {"_id": ObjectId(item_id)},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")

    updated_item = await db.items.find_one({"_id": ObjectId(item_id)})
    if updated_item:
        updated_item["_id"] = str(updated_item["_id"])
        return updated_item

    raise HTTPException(status_code=500, detail="Failed to retrieve updated item")


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: str):
    """Delete an item"""
    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=400, detail="Invalid item ID format")

    db = get_database()
    result = await db.items.delete_one({"_id": ObjectId(item_id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")

    return None

