#!/usr/bin/env python3
"""
User Management Script for ValidS Compliance System
This script allows you to create and manage users in the system.
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


async def create_user():
    """Create a new user"""
    client = None
    try:
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        db = client[settings.DATABASE_NAME]

        print("\n" + "="*50)
        print("Create New User")
        print("="*50)

        # Get user details
        username = input("Enter username: ").strip()
        if not username:
            print("Username cannot be empty!")
            return

        print("Available roles:")
        print("1. superadmin - Full system access")
        print("2. auditor - Can manage companies and users")
        print("3. spectator - Can view company progress")
        print("4. employee - Can submit compliance forms")

        role_choice = input("Select role (1-4): ").strip()
        role_map = {
            "1": "superadmin",
            "2": "auditor",
            "3": "spectator",
            "4": "employee"
        }

        if role_choice not in role_map:
            print("Invalid role selection!")
            return

        roletype = role_map[role_choice]

        email = input("Enter email: ").strip()
        if not email:
            print("Email cannot be empty!")
            return

        password = input("Enter password (min 6 characters): ").strip()
        if len(password) < 6:
            print("Password must be at least 6 characters long!")
            return

        company_id = None
        experience_years = None

        if roletype != "superadmin":
            company_id = input("Enter company ID (or press Enter to skip): ").strip()
            if company_id and not ObjectId.is_valid(company_id):
                print("Invalid company ID format!")
                return

            if roletype == "employee":
                exp_input = input("Enter years of experience (0-50): ").strip()
                if exp_input:
                    try:
                        experience_years = int(exp_input)
                        if not (0 <= experience_years <= 50):
                            print("Experience must be between 0 and 50 years!")
                            return
                    except ValueError:
                        print("Invalid experience value!")
                        return

        # Create user data
        user_data = {
            "username": username,
            "roletype": roletype,
            "email": email,
            "password": hash_password(password),
            "company_id": company_id if company_id else None,
            "experience_years": experience_years,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        # Insert user
        result = await db.users.insert_one(user_data)

        if result.inserted_id:
            print(f"\n✅ User '{username}' created successfully!")
            print(f"User ID: {result.inserted_id}")
            print(f"Role: {roletype}")
            print(f"Email: {email}")
        else:
            print("❌ Failed to create user")

    except Exception as e:
        logger.error(f"Error creating user: {e}")
        print(f"❌ Error: {e}")
    finally:
        if client:
            client.close()


async def list_users():
    """List all users in the system"""
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
            print("\n" + "="*80)
            print("EXISTING USERS IN SYSTEM")
            print("="*80)
            print(f"{'Username':<20} {'Email':<30} {'Role':<12} {'Company':<15} {'Active':<8}")
            print("-" * 80)

            for user in users:
                company = user.get('company_id', 'N/A')[:14] if user.get('company_id') else 'N/A'
                print(f"{user['username']:<20} {user['email']:<30} {user['roletype']:<12} {company:<15} {user['is_active']:<8}")

            print("="*80)
            print(f"Total users: {len(users)}")
        else:
            print("No users found in the system.")

    except Exception as e:
        logger.error(f"Error listing users: {e}")
    finally:
        if client:
            client.close()


async def create_sample_data():
    """Create sample data for testing"""
    client = None
    try:
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        db = client[settings.DATABASE_NAME]

        print("\n" + "="*50)
        print("Creating Sample Data")
        print("="*50)

        # Create sample ISO
        iso_data = {
            "iso_name": "ISO 27001",
            "iso_description": "Information Security Management System",
            "control_id": "sample_control_id",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        iso_result = await db.iso.insert_one(iso_data)
        print(f"✅ Created ISO: {iso_data['iso_name']} (ID: {iso_result.inserted_id})")

        # Create sample company
        company_data = {
            "company_name": "Sample Company",
            "company_description": "A sample company for testing",
            "user_id": "superadmin_id",  # This would be the superadmin's ID
            "iso_id": str(iso_result.inserted_id),
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        company_result = await db.companies.insert_one(company_data)
        print(f"✅ Created Company: {company_data['company_name']} (ID: {company_result.inserted_id})")

        # Create sample field
        field_data = {
            "field_name": "Security Level",
            "fieldType": "select",
            "isRequired": True,
            "options": ["Low", "Medium", "High", "Critical"],
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        field_result = await db.fields.insert_one(field_data)
        print(f"✅ Created Field: {field_data['field_name']} (ID: {field_result.inserted_id})")

        print("\nSample data created successfully!")
        print("You can now test the API endpoints with this data.")

    except Exception as e:
        logger.error(f"Error creating sample data: {e}")
        print(f"❌ Error: {e}")
    finally:
        if client:
            client.close()


async def main():
    """Main menu"""
    while True:
        print("\n" + "="*50)
        print("ValidS Compliance System - User Management")
        print("="*50)
        print("1. Create new user")
        print("2. List all users")
        print("3. Create sample data")
        print("4. Exit")

        choice = input("\nSelect an option (1-4): ").strip()

        if choice == "1":
            await create_user()
        elif choice == "2":
            await list_users()
        elif choice == "3":
            await create_sample_data()
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid option! Please select 1-4.")


if __name__ == "__main__":
    asyncio.run(main())
