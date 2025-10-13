# ValidS Backend API

FastAPI backend with MongoDB integration for the ValidS project.

## 🚀 Features

- **FastAPI** - Modern, fast web framework for building APIs
- **MongoDB** - NoSQL database with Motor (async driver)
- **Docker** - Containerized deployment
- **Pydantic** - Data validation using Python type annotations
- **CORS** - Cross-Origin Resource Sharing configured
- **RESTful API** - Complete CRUD operations
- **Auto Documentation** - Swagger UI and ReDoc

## 📋 Prerequisites

- Python 3.11+
- Docker & Docker Compose (for containerized deployment)
- MongoDB (local or remote instance)

## 🛠️ Setup

### Option 1: Local Development (without Docker)

1. **Create a virtual environment:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your MongoDB URL
   ```

4. **Run the application:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Option 2: Docker Deployment (Recommended)

1. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env if needed (MongoDB URL is pre-configured for Docker)
   ```

2. **Build and run with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

   This will start:
   - FastAPI application on `http://localhost:8000`
   - MongoDB on `localhost:27017`
   - Mongo Express (Web UI) on `http://localhost:8081`

3. **Run in detached mode:**
   ```bash
   docker-compose up -d
   ```

4. **Stop services:**
   ```bash
   docker-compose down
   ```

5. **Stop and remove volumes:**
   ```bash
   docker-compose down -v
   ```

## 📚 API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc
- **OpenAPI JSON**: http://localhost:8000/api/v1/openapi.json

## 🔌 API Endpoints

### Health Check
- `GET /` - Welcome message
- `GET /health` - Health check endpoint

### Items (CRUD Operations)
- `POST /api/v1/items/` - Create a new item
- `GET /api/v1/items/` - Get all items (with pagination)
- `GET /api/v1/items/{item_id}` - Get a single item
- `PUT /api/v1/items/{item_id}` - Update an item
- `DELETE /api/v1/items/{item_id}` - Delete an item

## 📝 Example Requests

### Create an Item
```bash
curl -X POST "http://localhost:8000/api/v1/items/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sample Item",
    "description": "This is a test item",
    "is_active": true
  }'
```

### Get All Items
```bash
curl "http://localhost:8000/api/v1/items/"
```

### Get Single Item
```bash
curl "http://localhost:8000/api/v1/items/{item_id}"
```

### Update Item
```bash
curl -X PUT "http://localhost:8000/api/v1/items/{item_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Item",
    "is_active": false
  }'
```

### Delete Item
```bash
curl -X DELETE "http://localhost:8000/api/v1/items/{item_id}"
```

## 🗂️ Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── api/                 # API routes
│   │   ├── __init__.py
│   │   └── items.py         # Items CRUD endpoints
│   ├── core/                # Core configuration
│   │   ├── __init__.py
│   │   └── config.py        # Settings and environment config
│   ├── db/                  # Database configuration
│   │   ├── __init__.py
│   │   └── mongodb.py       # MongoDB connection
│   └── models/              # Pydantic models
│       ├── __init__.py
│       └── item.py          # Item model
├── .env.example             # Example environment variables
├── .gitignore
├── .dockerignore
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker Compose configuration
├── requirements.txt         # Python dependencies
└── README.md
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017  # or your MongoDB URL
DATABASE_NAME=valids_db

# API Configuration
API_V1_PREFIX=/api/v1
PROJECT_NAME=ValidS API
DEBUG=True

# CORS Configuration
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 🔐 MongoDB Connection

### Local MongoDB
```env
MONGODB_URL=mongodb://localhost:27017
```

### MongoDB Atlas (Cloud)
```env
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/
```

### Docker MongoDB
```env
MONGODB_URL=mongodb://mongo:27017
```

## 🧪 Testing the API

You can test the API using:
- **Swagger UI** at http://localhost:8000/api/v1/docs
- **cURL** (see example requests above)
- **Postman** or **Insomnia**
- **Python requests library**

## 📦 Dependencies

Key dependencies:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `motor` - Async MongoDB driver
- `pymongo` - MongoDB driver
- `pydantic` - Data validation
- `python-dotenv` - Environment variable management

## 🚢 Deployment

### Production Considerations

1. **Change SECRET_KEY** in `.env` to a secure random string
2. **Set DEBUG=False** in production
3. **Use a managed MongoDB service** (MongoDB Atlas, AWS DocumentDB, etc.)
4. **Enable authentication** on MongoDB
5. **Use HTTPS** with SSL certificates
6. **Set up monitoring and logging**
7. **Configure proper CORS origins**

## 🐛 Troubleshooting

### MongoDB Connection Issues
- Ensure MongoDB is running
- Check the `MONGODB_URL` in your `.env` file
- Verify network connectivity to MongoDB

### Docker Issues
- Ensure Docker Desktop is running
- Check if ports 8000, 8081, 27017 are not in use
- Run `docker-compose logs` to view logs

## 📄 License

This project is part of the ValidS application.

## 🤝 Contributing

For contributions, please follow the project's coding standards and create pull requests.

