#!/bin/bash

# ValidS Backend Stop Script

echo "🛑 Stopping ValidS Backend services..."
echo ""

# Stop Docker containers
docker-compose down

echo ""
echo "✅ All services stopped"
echo ""
echo "To remove volumes (database data): docker-compose down -v"

