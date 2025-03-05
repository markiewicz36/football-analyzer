import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
from dotenv import load_dotenv

from app.api import api_router
from app.db.init_db import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log")
    ]
)

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Football Analyzer API",
    description="API for football matches analysis with AI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with actual frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api")


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to Football Analyzer API",
        "status": "running",
        "documentation": "/docs"
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy"
    }


# Run database initialization on startup
@app.on_event("startup")
async def startup_event():
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialization completed")


# Run cleanup on shutdown
@app.on_event("shutdown")
async def shutdown_event():
    # Close any open connections/resources
    from app.services.football_api import football_api_client
    from app.services.deepseek_api import deepseek_client

    logger.info("Closing API client connections...")
    await football_api_client.close()
    await deepseek_client.close()
    logger.info("Shutdown completed")


# Run app
if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting application server on {host}:{port}")
    uvicorn.run("main:app", host=host, port=port, reload=True)