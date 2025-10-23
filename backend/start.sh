#!/bin/bash

# ValidS Backend Startup Script with Auto Superuser Creation

echo "🚀 Starting ValidS Backend..."
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cat > .env << EOF
# Database Configuration
MONGODB_URL=mongodb://mongo:27017
DATABASE_NAME=valids_db

# API Configuration
API_V1_PREFIX=/api/v1
PROJECT_NAME=ValidS API
DEBUG=True

# CORS Configuration
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:3001","http://localhost:8080"]
EOF
    echo "✅ .env file created"
    echo ""
fi

# Check if running with Docker
if [ "$1" = "docker" ]; then
    echo "🐳 Starting with Docker Compose..."
    docker-compose up --build
elif [ "$1" = "docker-detached" ]; then
    echo "🐳 Starting with Docker Compose (detached mode)..."
    docker-compose up -d --build

    echo ""
    echo "⏳ Waiting for services to start..."
    sleep 10

    echo "🔧 Creating superuser if it doesn't exist..."
    docker-compose exec -T api python -c "
import asyncio
import hashlib
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

async def ensure_superuser():
    try:
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        db = client[settings.DATABASE_NAME]

        # Check if superadmin exists
        existing = await db.users.find_one({'roletype': 'superadmin'})
        if existing:
            print('✅ Superadmin already exists!')
            print(f'Username: {existing[\"username\"]}')
            print(f'Email: {existing[\"email\"]}')
        else:
            # Create default superadmin
            superadmin_data = {
                'username': 'superadmin',
                'roletype': 'superadmin',
                'email': 'admin@valids.com',
                'password': hashlib.sha256('admin123'.encode()).hexdigest(),
                'company_id': None,
                'experience_years': None,
                'is_active': True,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }

            result = await db.users.insert_one(superadmin_data)
            print('✅ Default superadmin created!')
            print('Username: superadmin')
            print('Email: admin@valids.com')
            print('Password: admin123')
            print('⚠️  Please change the default password!')

        client.close()
    except Exception as e:
        print(f'❌ Error creating superuser: {e}')

asyncio.run(ensure_superuser())
"

    echo ""
    echo "✅ Services started in background"
    echo "📚 API Documentation: http://localhost:8000/api/v1/docs"
    echo "🗄️  Mongo Express: http://localhost:8081"
    echo "🔐 Default Superadmin: superadmin / admin123"
    echo ""
    echo "To view logs: docker-compose logs -f"
    echo "To stop: docker-compose down"
    echo "To create more users: docker-compose exec api python manage_users.py"

else
    echo "💻 Starting local development server..."
    echo ""

    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "📦 Creating virtual environment..."
        python3 -m venv venv
    fi

    # Activate virtual environment
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate

    # Install/update dependencies
    echo "📚 Installing dependencies..."
    pip install -q -r requirements.txt

    echo ""
    echo "✅ Starting FastAPI server..."
    echo "📚 API Documentation: http://localhost:8000/api/v1/docs"
    echo ""

    # Start the server
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
fi