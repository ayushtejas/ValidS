# ValidS Setup Guide

Follow these steps to get your full-stack application running.

## ✅ Prerequisites Checklist

- [ ] Node.js 18+ installed
- [ ] Python 3.11+ installed
- [ ] Docker Desktop installed (for backend)
- [ ] MongoDB URL ready (Atlas or local)
- [ ] Git configured

## 🚀 Step-by-Step Setup

### Step 1: Configure MongoDB URL

The backend needs a MongoDB connection. Edit the `.env` file:

```bash
cd backend
nano .env  # or code .env or vim .env
```

**Replace this line with your MongoDB URL:**
```env
MONGODB_URL=your-mongodb-url-here
```

**Examples:**

For **MongoDB Atlas** (Cloud):
```env
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/valids_db?retryWrites=true&w=majority
```

For **Local MongoDB**:
```env
MONGODB_URL=mongodb://localhost:27017
```

For **Docker** (default, no change needed):
```env
MONGODB_URL=mongodb://mongo:27017
```

### Step 2: Start the Backend

Choose one of these options:

#### Option A: Docker (Recommended) ⭐

```bash
cd backend

# Start all services (FastAPI + MongoDB + Mongo Express)
./start.sh docker

# Or in detached mode (runs in background)
./start.sh docker-detached
```

This will start:
- ✅ FastAPI backend on port 8000
- ✅ MongoDB on port 27017
- ✅ Mongo Express (DB Admin UI) on port 8081

#### Option B: Local Development

```bash
cd backend

# Creates venv, installs dependencies, and starts server
./start.sh
```

**Verify backend is running:**
- Visit http://localhost:8000/health
- You should see: `{"status": "healthy"}`

### Step 3: Start the Frontend

Open a **new terminal window**:

```bash
cd valids
npm install
npm run dev
```

**Verify frontend is running:**
- Visit http://localhost:3000
- You should see the Next.js app with shadcn/ui buttons

### Step 4: Test the API

Visit the interactive API documentation:
- **Swagger UI**: http://localhost:8000/api/v1/docs

Try creating an item:
1. Click on `POST /api/v1/items/`
2. Click "Try it out"
3. Use this example:
   ```json
   {
     "name": "My First Item",
     "description": "Testing the API",
     "is_active": true
   }
   ```
4. Click "Execute"
5. You should get a 201 response with the created item

### Step 5: View Your Database (Optional)

If using Docker, visit Mongo Express:
- **URL**: http://localhost:8081
- **Username**: `admin`
- **Password**: `admin`

You can browse your database collections and documents here.

## 🎯 Quick Commands Reference

### Backend Commands
```bash
# Start with Docker
cd backend && ./start.sh docker

# Start with Docker (background)
cd backend && ./start.sh docker-detached

# Start local development
cd backend && ./start.sh

# Stop Docker services
cd backend && ./stop.sh

# View Docker logs
cd backend && docker-compose logs -f

# Restart backend
cd backend && docker-compose restart api
```

### Frontend Commands
```bash
# Install dependencies
cd valids && npm install

# Start development server
cd valids && npm run dev

# Build for production
cd valids && npm run build

# Start production server
cd valids && npm start

# Add new shadcn component
cd valids && npx shadcn@latest add [component-name]
```

### Both Services
```bash
# Terminal 1: Backend
cd backend && ./start.sh docker-detached

# Terminal 2: Frontend
cd valids && npm run dev
```

## 🌐 Service URLs

Once everything is running:

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | Next.js app |
| Backend API | http://localhost:8000 | FastAPI root |
| API Docs | http://localhost:8000/api/v1/docs | Swagger UI |
| Health Check | http://localhost:8000/health | Backend health |
| MongoDB | localhost:27017 | Database |
| Mongo Express | http://localhost:8081 | DB Admin UI |

## 🧪 Testing Your Setup

### Test 1: Backend Health
```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy"}
```

### Test 2: Create an Item
```bash
curl -X POST "http://localhost:8000/api/v1/items/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Item",
    "description": "Testing the API",
    "is_active": true
  }'
```

### Test 3: Get All Items
```bash
curl http://localhost:8000/api/v1/items/
# Expected: Array of items (including the one you just created)
```

### Test 4: Frontend
- Visit http://localhost:3000
- You should see multiple button styles (Default, Secondary, Destructive, etc.)
- Try toggling dark mode in your system preferences

## 🔧 Troubleshooting

### Backend Issues

**Problem**: "Connection refused" or MongoDB errors
**Solution**:
- Check if MongoDB is running
- Verify `MONGODB_URL` in `backend/.env`
- If using Docker: `docker-compose down && docker-compose up`

**Problem**: Port 8000 already in use
**Solution**:
```bash
# Find and kill process using port 8000
lsof -ti:8000 | xargs kill -9
```

### Frontend Issues

**Problem**: Module not found errors
**Solution**:
```bash
cd valids
rm -rf node_modules package-lock.json
npm install
```

**Problem**: Port 3000 already in use
**Solution**:
```bash
# Find and kill process using port 3000
lsof -ti:3000 | xargs kill -9
```

### Docker Issues

**Problem**: Docker containers won't start
**Solution**:
1. Ensure Docker Desktop is running
2. Check available ports: `lsof -i :8000 -i :8081 -i :27017`
3. Restart Docker Desktop
4. Try: `docker-compose down -v && docker-compose up --build`

**Problem**: Permission denied errors
**Solution**:
```bash
cd backend
chmod +x start.sh stop.sh
```

## 📝 Next Steps

After setup is complete:

1. **Customize the Frontend**
   - Edit `valids/src/app/page.tsx`
   - Add more shadcn/ui components
   - Create new pages in `valids/src/app/`

2. **Extend the Backend**
   - Add new models in `backend/app/models/`
   - Create new endpoints in `backend/app/api/`
   - Add authentication/authorization

3. **Connect Frontend to Backend**
   - Use `fetch` or `axios` to call APIs
   - Create API client in `valids/src/lib/api.ts`
   - Add environment variables for API URL

4. **Deploy**
   - Frontend: Deploy to Vercel
   - Backend: Deploy Docker container to cloud

## 🎓 Learning Resources

- **Next.js**: https://nextjs.org/docs
- **shadcn/ui**: https://ui.shadcn.com/
- **Tailwind CSS**: https://tailwindcss.com/docs
- **FastAPI**: https://fastapi.tiangolo.com/
- **MongoDB**: https://www.mongodb.com/docs/

## ✅ Setup Complete!

You now have:
- ✅ Next.js frontend with shadcn/ui and Tailwind CSS
- ✅ FastAPI backend with MongoDB
- ✅ Dockerized backend services
- ✅ Interactive API documentation
- ✅ Full CRUD operations
- ✅ Development-ready environment

Happy coding! 🚀

