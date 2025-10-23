#!/usr/bin/env python3
"""
Script to create a superadmin user for the ValidS compliance system.
Run this script to create the initial superadmin user.
"""

import asyncio
import hashlib
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


async def create_superuser():
    """Create a superadmin user"""
    client = None
    try:
        # Connect to MongoDB
        logger.info(f"Connecting to MongoDB at {settings.MONGODB_URL}")
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        db = client[settings.DATABASE_NAME]

        # Test connection
        await client.admin.command('ping')
        logger.info(f"Successfully connected to MongoDB database: {settings.DATABASE_NAME}")

        # Check if superadmin already exists
        existing_superadmin = await db.users.find_one({"roletype": "superadmin"})
        if existing_superadmin:
            logger.warning("Superadmin user already exists!")
            print(f"Superadmin username: {existing_superadmin['username']}")
            print(f"Superadmin email: {existing_superadmin['email']}")
            return

        # Get superadmin details from user input
        print("\n" + "="*50)
        print("Creating Superadmin User for ValidS Compliance System")
        print("="*50)

        username = input("Enter superadmin username: ").strip()
        if not username:
            print("Username cannot be empty!")
            return

        email = input("Enter superadmin email: ").strip()
        if not email:
            print("Email cannot be empty!")
            return

        password = input("Enter superadmin password (min 6 characters): ").strip()
        if len(password) < 6:
            print("Password must be at least 6 characters long!")
            return

        # Create superadmin user
        superadmin_data = {
            "username": username,
            "roletype": "superadmin",
            "email": email,
            "password": hash_password(password),
            "company_id": None,  # Superadmin doesn't belong to any company
            "experience_years": None,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        # Insert superadmin user
        result = await db.users.insert_one(superadmin_data)

        if result.inserted_id:
            logger.info("✅ Superadmin user created successfully!")
            print("\n" + "="*50)
            print("SUPERADMIN USER CREATED SUCCESSFULLY")
            print("="*50)
            print(f"Username: {username}")
            print(f"Email: {email}")
            print(f"Role: superadmin")
            print(f"User ID: {result.inserted_id}")
            print("\nYou can now use these credentials to:")
            print("1. Onboard auditors")
            print("2. Manage companies")
            print("3. Access the API at http://localhost:8000/api/v1/docs")
            print("="*50)
        else:
            logger.error("❌ Failed to create superadmin user")

    except Exception as e:
        logger.error(f"Error creating superadmin: {e}")
        print(f"❌ Error: {e}")
    finally:
        if client:
            client.close()
            logger.info("MongoDB connection closed")


async def list_existing_users():
    """List existing users in the system"""
    client = None
    try:
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        db = client[settings.DATABASE_NAME]

        users = []
        cursor = db.users.find({})
        async for user in cursor:
            user["_id"] = str(user["_id"])
            # Remove password from display
            if "password" in user:
                del user["password"]
            users.append(user)

        if users:
            print("\n" + "="*50)
            print("EXISTING USERS IN SYSTEM")
            print("="*50)
            for user in users:
                print(f"Username: {user['username']}")
                print(f"Email: {user['email']}")
                print(f"Role: {user['roletype']}")
                print(f"Active: {user['is_active']}")
                print("-" * 30)
        else:
            print("No users found in the system.")

    except Exception as e:
        logger.error(f"Error listing users: {e}")
    finally:
        if client:
            client.close()


if __name__ == "__main__":
    print("ValidS Compliance System - Superuser Creation")
    print("=" * 50)

    # Check if user wants to list existing users first
    list_users = input("Do you want to see existing users first? (y/n): ").strip().lower()
    if list_users == 'y':
        asyncio.run(list_existing_users())

    # Create superuser
    asyncio.run(create_superuser())
