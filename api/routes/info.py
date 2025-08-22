from fastapi import APIRouter
from config.settings import settings

router = APIRouter()


@router.get("/info")
async def get_info():
    """Get application information"""
    return {
        "app_name": getattr(settings, 'app_name', 'Valuation API'),
        "version": getattr(settings, 'version', '1.0.0'),
        "description": "API for item valuation and estimation management"
    }


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}