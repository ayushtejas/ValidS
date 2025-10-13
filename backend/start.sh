#!/bin/bash

# ValidS Backend Startup Script

echo "🚀 Starting ValidS Backend..."
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file and add your MongoDB URL"
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
    echo "✅ Services started in background"
    echo "📚 API Documentation: http://localhost:8000/api/v1/docs"
    echo "🗄️  Mongo Express: http://localhost:8081"
    echo ""
    echo "To view logs: docker-compose logs -f"
    echo "To stop: docker-compose down"
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

