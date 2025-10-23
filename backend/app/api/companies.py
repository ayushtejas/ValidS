from fastapi import APIRouter, HTTPException, status
from typing import List
from datetime import datetime
from bson import ObjectId

from app.models.company import CompanyCreate, CompanyUpdate, CompanyResponse
from app.db.mongodb import get_database

router = APIRouter()


@router.post("/", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company(company: CompanyCreate):
    """Create a new company"""
    db = get_database()

    # Validate that user exists
    if not ObjectId.is_valid(company.user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    user_exists = await db.users.find_one({"_id": ObjectId(company.user_id)})
    if not user_exists:
        raise HTTPException(status_code=404, detail="User not found")

    # Validate that ISO exists
    if not ObjectId.is_valid(company.iso_id):
        raise HTTPException(status_code=400, detail="Invalid ISO ID format")

    iso_exists = await db.iso.find_one({"_id": ObjectId(company.iso_id)})
    if not iso_exists:
        raise HTTPException(status_code=404, detail="ISO not found")

    company_dict = company.model_dump()
    company_dict["created_at"] = datetime.utcnow()
    company_dict["updated_at"] = datetime.utcnow()

    result = await db.companies.insert_one(company_dict)
    created_company = await db.companies.find_one({"_id": result.inserted_id})

    if created_company:
        created_company["_id"] = str(created_company["_id"])
        return created_company

    raise HTTPException(status_code=500, detail="Failed to create company")


@router.get("/", response_model=List[CompanyResponse])
async def get_companies(skip: int = 0, limit: int = 100):
    """Get all companies with pagination"""
    db = get_database()

    companies = []
    cursor = db.companies.find().skip(skip).limit(limit)

    async for document in cursor:
        document["_id"] = str(document["_id"])
        companies.append(document)

    return companies


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(company_id: str):
    """Get a single company by ID"""
    if not ObjectId.is_valid(company_id):
        raise HTTPException(status_code=400, detail="Invalid company ID format")

    db = get_database()
    company = await db.companies.find_one({"_id": ObjectId(company_id)})

    if company:
        company["_id"] = str(company["_id"])
        return company

    raise HTTPException(status_code=404, detail="Company not found")


@router.get("/user/{user_id}", response_model=List[CompanyResponse])
async def get_companies_by_user(user_id: str):
    """Get all companies for a specific user"""
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    db = get_database()
    companies = []
    cursor = db.companies.find({"user_id": user_id})

    async for document in cursor:
        document["_id"] = str(document["_id"])
        companies.append(document)

    return companies


@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(company_id: str, company_update: CompanyUpdate):
    """Update a company"""
    if not ObjectId.is_valid(company_id):
        raise HTTPException(status_code=400, detail="Invalid company ID format")

    db = get_database()

    # Validate user_id if provided
    if company_update.user_id and not ObjectId.is_valid(company_update.user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    if company_update.user_id:
        user_exists = await db.users.find_one({"_id": ObjectId(company_update.user_id)})
        if not user_exists:
            raise HTTPException(status_code=404, detail="User not found")

    # Validate iso_id if provided
    if company_update.iso_id and not ObjectId.is_valid(company_update.iso_id):
        raise HTTPException(status_code=400, detail="Invalid ISO ID format")

    if company_update.iso_id:
        iso_exists = await db.iso.find_one({"_id": ObjectId(company_update.iso_id)})
        if not iso_exists:
            raise HTTPException(status_code=404, detail="ISO not found")

    # Only update fields that are provided
    update_data = {k: v for k, v in company_update.model_dump(exclude_unset=True).items()}

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    update_data["updated_at"] = datetime.utcnow()

    result = await db.companies.update_one(
        {"_id": ObjectId(company_id)},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Company not found")

    updated_company = await db.companies.find_one({"_id": ObjectId(company_id)})
    if updated_company:
        updated_company["_id"] = str(updated_company["_id"])
        return updated_company

    raise HTTPException(status_code=500, detail="Failed to retrieve updated company")


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(company_id: str):
    """Delete a company"""
    if not ObjectId.is_valid(company_id):
        raise HTTPException(status_code=400, detail="Invalid company ID format")

    db = get_database()
    result = await db.companies.delete_one({"_id": ObjectId(company_id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Company not found")

    return None
