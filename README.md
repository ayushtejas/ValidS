# ValidS Full Stack Application

A modern full-stack application with Next.js frontend and FastAPI backend.

## 📁 Project Structure

```
ValidS/
├── valids/              # Next.js Frontend
│   ├── src/
│   │   ├── app/        # App Router pages
│   │   ├── components/ # React components
│   │   └── lib/        # Utility functions
│   ├── public/         # Static assets
│   └── ...
│
└── backend/            # FastAPI Backend
    ├── app/
    │   ├── api/       # API routes
    │   ├── models/    # Data models
    │   ├── core/      # Configuration
    │   └── db/        # Database connection
    ├── Dockerfile
    ├── docker-compose.yml
    └── ...
```

## 🚀 Tech Stack

### Frontend (Next.js)
- **Next.js 15.5.4** - React framework with App Router
- **React 19** - Latest React version
- **TypeScript** - Type safety
- **Tailwind CSS v4** - Utility-first CSS framework
- **shadcn/ui** - Beautiful UI components

### Backend (FastAPI)
- **FastAPI** - Modern Python web framework
- **MongoDB** - NoSQL database
- **Motor** - Async MongoDB driver
- **Pydantic** - Data validation
- **Docker** - Containerization

## 🛠️ Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- Docker & Docker Compose (recommended for backend)

### Frontend Setup

```bash
cd valids
npm install
npm run dev
```

Frontend will be available at **http://localhost:3000**

See [valids/README.md](./valids/README.md) for more details.

### Backend Setup

#### Option 1: Docker (Recommended)

```bash
cd backend

# Add your MongoDB URL to .env file
nano .env  # or use any text editor

# Start all services (FastAPI + MongoDB + Mongo Express)
./start.sh docker

# Or run in detached mode
./start.sh docker-detached
```

#### Option 2: Local Development

```bash
cd backend

# Add your MongoDB URL to .env file
nano .env

# Start the backend (creates venv, installs deps, runs server)
./start.sh
```

Backend will be available at:
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/v1/docs
- **Mongo Express**: http://localhost:8081 (Docker only)

See [backend/README.md](./backend/README.md) for more details.

## 🔧 Configuration

### MongoDB URL Setup

1. **Edit the backend `.env` file:**
   ```bash
   cd backend
   nano .env
   ```

2. **Add your MongoDB URL:**

   For local MongoDB:
   ```env
   MONGODB_URL=mongodb://localhost:27017
   ```

   For MongoDB Atlas:
   ```env
   MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/
   ```

   For Docker (already configured):
   ```env
   MONGODB_URL=mongodb://mongo:27017
   ```

3. **Save and restart the backend**

## 📚 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc

## 🐳 Docker Commands

### Start Services
```bash
cd backend
docker-compose up          # Start with logs
docker-compose up -d       # Start in background
docker-compose up --build  # Rebuild and start
```

### Stop Services
```bash
docker-compose down        # Stop services
docker-compose down -v     # Stop and remove volumes (deletes data)
```

### View Logs
```bash
docker-compose logs        # All logs
docker-compose logs -f api # Follow API logs
```

### Useful Commands
```bash
# Or use the helper scripts
./start.sh docker          # Start with Docker
./stop.sh                  # Stop all services
```

## 🔗 Available Endpoints

### Frontend
- Home: http://localhost:3000

### Backend
- API Root: http://localhost:8000
- Health Check: http://localhost:8000/health
- API Documentation: http://localhost:8000/api/v1/docs
- Items CRUD: http://localhost:8000/api/v1/items/

### Database
- MongoDB: localhost:27017
- Mongo Express UI: http://localhost:8081 (Docker only)
  - Username: `admin`
  - Password: `admin`

## 📝 Development Workflow

1. **Start the backend:**
   ```bash
   cd backend
   ./start.sh docker-detached
   ```

2. **Start the frontend:**
   ```bash
   cd valids
   npm run dev
   ```

3. **Make changes** - Both support hot reloading

4. **Test the API** at http://localhost:8000/api/v1/docs

5. **View the frontend** at http://localhost:3000

## 🧪 Testing the Stack

### Test Backend
```bash
# Health check
curl http://localhost:8000/health

# Create an item
curl -X POST "http://localhost:8000/api/v1/items/" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Item","description":"Testing API","is_active":true}'

# Get all items
curl http://localhost:8000/api/v1/items/
```

### Test Frontend
Visit http://localhost:3000 and see the shadcn/ui button examples.

## 🚢 Deployment

### Frontend (Vercel)
```bash
cd valids
vercel deploy
```

### Backend (Docker)
The backend is Docker-ready. Deploy to:
- AWS ECS/Fargate
- Google Cloud Run
- Azure Container Instances
- Any Docker-compatible platform

## 📦 Project Files

### Root Level
- `README.md` - This file
- `valids/` - Next.js frontend
- `backend/` - FastAPI backend

### Frontend (valids/)
- `src/app/` - Next.js pages
- `src/components/ui/` - shadcn/ui components
- `src/lib/utils.ts` - Utility functions
- `components.json` - shadcn/ui config

### Backend (backend/)
- `app/main.py` - FastAPI entry point
- `app/api/` - API routes
- `app/models/` - Pydantic models
- `app/db/mongodb.py` - Database connection
- `Dockerfile` - Docker configuration
- `docker-compose.yml` - Multi-container setup

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test both frontend and backend
5. Submit a pull request

## 📄 License

This project is part of the ValidS application.

## 🆘 Troubleshooting

### Backend won't start
- Check if MongoDB is running
- Verify `MONGODB_URL` in `.env`
- Check if port 8000 is available

### Frontend won't start
- Run `npm install` in the valids directory
- Check if port 3000 is available
- Clear `.next` cache: `rm -rf .next`

### Docker issues
- Ensure Docker Desktop is running
- Check port availability (8000, 8081, 27017)
- View logs: `docker-compose logs`

## 📞 Support

For issues or questions, please create an issue in the repository.

---

**Made with ❤️ using Next.js, FastAPI, and MongoDB**

