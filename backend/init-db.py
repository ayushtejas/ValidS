#!/usr/bin/env python3
"""
Database initialization script for ValidS Compliance System
This script runs automatically when the container starts to ensure
a superadmin user exists.
"""

import asyncio
import hashlib
import logging
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


async def ensure_superuser():
    """Ensure a superadmin user exists"""
    client = None
    try:
        logger.info("Connecting to MongoDB...")
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        db = client[settings.DATABASE_NAME]

        # Test connection
        await client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")

        # Check if superadmin exists
        existing_superadmin = await db.users.find_one({"roletype": "superadmin"})

        if existing_superadmin:
            logger.info("✅ Superadmin already exists!")
            logger.info(f"Username: {existing_superadmin['username']}")
            logger.info(f"Email: {existing_superadmin['email']}")
            return existing_superadmin

        # Create default superadmin
        logger.info("Creating default superadmin user...")

        superadmin_data = {
            "username": "superadmin",
            "roletype": "superadmin",
            "email": "admin@valids.com",
            "password": hash_password("admin123"),
            "company_id": None,
            "experience_years": None,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        result = await db.users.insert_one(superadmin_data)

        if result.inserted_id:
            logger.info("✅ Default superadmin created successfully!")
            logger.info("Username: superadmin")
            logger.info("Email: admin@valids.com")
            logger.info("Password: admin123")
            logger.warning("⚠️  Please change the default password in production!")
            return superadmin_data
        else:
            logger.error("❌ Failed to create superadmin")
            return None

    except Exception as e:
        logger.error(f"❌ Error ensuring superuser: {e}")
        return None
    finally:
        if client:
            client.close()


async def create_sample_data():
    """Create sample data for testing"""
    client = None
    try:
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        db = client[settings.DATABASE_NAME]

        # Check if sample data already exists
        existing_iso = await db.iso.find_one({"iso_name": "ISO 27001"})
        if existing_iso:
            logger.info("Sample data already exists, skipping...")
            return

        logger.info("Creating sample data...")

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
        logger.info(f"✅ Created sample field: {field_data['field_name']}")

        # Create sample question
        question_data = {
            "description": "What is the current security level of your organization?",
            "fields_id": str(field_result.inserted_id),
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        question_result = await db.questions.insert_one(question_data)
        logger.info(f"✅ Created sample question: {question_data['description'][:50]}...")

        # Create sample control
        control_data = {
            "control_name": "Access Control Management",
            "control_key": "AC-01",
            "question_id": str(question_result.inserted_id),
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        control_result = await db.controls.insert_one(control_data)
        logger.info(f"✅ Created sample control: {control_data['control_name']}")

        # Create sample ISO
        iso_data = {
            "iso_name": "ISO 27001",
            "iso_description": "Information Security Management System",
            "control_id": str(control_result.inserted_id),
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        iso_result = await db.iso.insert_one(iso_data)
        logger.info(f"✅ Created sample ISO: {iso_data['iso_name']}")

        logger.info("✅ Sample data created successfully!")

    except Exception as e:
        logger.error(f"❌ Error creating sample data: {e}")
    finally:
        if client:
            client.close()


async def main():
    """Main initialization function"""
    logger.info("🚀 Initializing ValidS Database...")

    # Ensure superuser exists
    superuser = await ensure_superuser()

    if superuser:
        # Create sample data for testing
        await create_sample_data()
        logger.info("✅ Database initialization completed!")
    else:
        logger.error("❌ Database initialization failed!")


if __name__ == "__main__":
    asyncio.run(main())
