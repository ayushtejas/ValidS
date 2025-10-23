from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.config import settings
from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.api import items, users, companies, iso, controls, questions, fields, submissions, assignments, admin

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Connect to MongoDB on startup"""
    logger.info("Starting up...")
    await connect_to_mongo()
    logger.info("Application started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Close MongoDB connection on shutdown"""
    logger.info("Shutting down...")
    await close_mongo_connection()
    logger.info("Application shut down successfully")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to ValidS API",
        "docs": f"{settings.API_V1_PREFIX}/docs",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# Include routers
app.include_router(
    items.router,
    prefix=f"{settings.API_V1_PREFIX}/items",
    tags=["items"]
)

app.include_router(
    users.router,
    prefix=f"{settings.API_V1_PREFIX}/users",
    tags=["users"]
)

app.include_router(
    companies.router,
    prefix=f"{settings.API_V1_PREFIX}/companies",
    tags=["companies"]
)

app.include_router(
    iso.router,
    prefix=f"{settings.API_V1_PREFIX}/iso",
    tags=["iso"]
)

app.include_router(
    controls.router,
    prefix=f"{settings.API_V1_PREFIX}/controls",
    tags=["controls"]
)

app.include_router(
    questions.router,
    prefix=f"{settings.API_V1_PREFIX}/questions",
    tags=["questions"]
)

app.include_router(
    fields.router,
    prefix=f"{settings.API_V1_PREFIX}/fields",
    tags=["fields"]
)

app.include_router(
    submissions.router,
    prefix=f"{settings.API_V1_PREFIX}/submissions",
    tags=["submissions"]
)

app.include_router(
    assignments.router,
    prefix=f"{settings.API_V1_PREFIX}/assignments",
    tags=["assignments"]
)

app.include_router(
    admin.router,
    prefix=f"{settings.API_V1_PREFIX}/admin",
    tags=["admin"]
)

