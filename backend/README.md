# ValidS Compliance System - Backend

A comprehensive compliance forms submission system with role-based access control for managing ISO standards, company compliance, and user submissions.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Git

### 1. Clone and Navigate
```bash
git clone <your-repo-url>
cd ValidS/backend
```

### 2. Build and Start (Automated)
```bash
# Option 1: Using the startup script (Recommended)
./start.sh docker-detached

# Option 2: Direct Docker Compose
docker-compose up -d --build
```

### 3. Access the System
- **API Documentation:** http://localhost:8000/api/v1/docs
- **Database Admin:** http://localhost:8081 (admin/admin)
- **Health Check:** http://localhost:8000/health

## 🔐 Default Credentials

The system automatically creates a superadmin user:

- **Username:** `superadmin`
- **Email:** `admin@valids.com`
- **Password:** `admin123`
- **Role:** `superadmin`

⚠️ **Important:** Change the default password in production!

## 🏗️ Build Options

### Docker (Recommended)
```bash
# Build and start in background
./start.sh docker-detached

# Build and start with logs
./start.sh docker

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild from scratch
docker-compose down -v
docker-compose up -d --build
```

### Local Development
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start development server
./start.sh
```

## 📊 System Architecture

```
SUPERADMIN
    ↓ (onboards)
AUDITOR
    ↓ (onboards companies & users)
COMPANY
    ├── SPECTATOR (monitors progress)
    ├── EMPLOYEE (submits forms)
    └── AUDITOR (manages company)
```

## 🔧 User Management

### Create Additional Users
```bash
# Using the management script
docker-compose exec api python manage_users.py

# Using API endpoint
curl -X POST "http://localhost:8000/api/v1/admin/create-superadmin" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "new_admin",
    "email": "new@company.com",
    "password": "secure_password"
  }'
```

### System Status
```bash
curl http://localhost:8000/api/v1/admin/system-status
```

## 🌐 API Endpoints

### Authentication & Users
- `POST /api/v1/users/` - Create users
- `GET /api/v1/users/` - List users
- `POST /api/v1/admin/create-superadmin` - Create superadmin

### Companies & Compliance
- `POST /api/v1/companies/` - Create companies
- `GET /api/v1/companies/` - List companies
- `POST /api/v1/submissions/` - Submit compliance forms
- `GET /api/v1/submissions/company/{id}/progress` - View progress

### Question Management
- `GET /api/v1/assignments/questions/role-based` - Get role-specific questions
- `POST /api/v1/assignments/questions/assign` - Assign questions to users

## 🗄️ Database Collections

- **users** - User accounts with roles
- **companies** - Company information
- **iso** - ISO standards and controls
- **controls** - Security controls
- **questions** - Compliance questions
- **fields** - Question field types
- **submissions** - Form submissions
- **question_assignments** - User-question assignments

## 🔒 Security Features

- **Role-based access control** (superadmin, auditor, spectator, employee)
- **Company-level data isolation**
- **Password hashing** with SHA-256
- **Input validation** and sanitization
- **Authentication** system (ready for JWT)

## 🛠️ Development

### Project Structure
```
backend/
├── app/
│   ├── api/           # API endpoints
│   ├── core/          # Configuration and auth
│   ├── db/            # Database connection
│   ├── models/        # Pydantic models
│   └── main.py        # FastAPI application
├── docker-compose.yml # Docker services
├── Dockerfile         # Container configuration
├── requirements.txt   # Python dependencies
├── start.sh          # Startup script
├── init-db.py        # Database initialization
└── manage_users.py    # User management script
```

### Environment Variables
```bash
MONGODB_URL=mongodb://mongo:27017
DATABASE_NAME=valids_db
API_V1_PREFIX=/api/v1
PROJECT_NAME=ValidS API
DEBUG=True
```

## 🚨 Troubleshooting

### Common Issues

1. **Port conflicts:**
   ```bash
   # Check if ports are in use
   lsof -i :8000
   lsof -i :27017
   lsof -i :8081
   ```

2. **Database connection issues:**
   ```bash
   # Check MongoDB logs
   docker-compose logs mongo

   # Restart database
   docker-compose restart mongo
   ```

3. **API not starting:**
   ```bash
   # Check API logs
   docker-compose logs api

   # Rebuild container
   docker-compose up -d --build --force-recreate
   ```

4. **Permission issues:**
   ```bash
   # Fix script permissions
   chmod +x start.sh
   chmod +x manage_users.py
   ```

### Reset Everything
```bash
# Stop and remove all containers and volumes
docker-compose down -v

# Remove all images
docker system prune -a

# Start fresh
./start.sh docker-detached
```

## 📈 Monitoring

### Health Checks
- **API Health:** http://localhost:8000/health
- **Database Health:** http://localhost:8081
- **System Status:** http://localhost:8000/api/v1/admin/system-status

### Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f mongo
```

## 🔄 Updates

### Update Dependencies
```bash
# Rebuild with latest dependencies
docker-compose down
docker-compose up -d --build
```

### Database Migrations
The system automatically handles database initialization and user creation on startup.

## 📞 Support

For issues and questions:
1. Check the logs: `docker-compose logs -f`
2. Verify system status: `curl http://localhost:8000/api/v1/admin/system-status`
3. Check API documentation: http://localhost:8000/api/v1/docs

---

**ValidS Compliance System** - Ready for production use! 🎯