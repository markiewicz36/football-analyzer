from fastapi import APIRouter
from .fixtures import router as fixtures_router
from .statistics import router as statistics_router

api_router = APIRouter()

# Add routes
api_router.include_router(fixtures_router)
api_router.include_router(statistics_router)