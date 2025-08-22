from contextlib import asynccontextmanager
from fastapi import FastAPI

from config.settings import settings
from database.connection import create_db_and_tables
from api.routes import info, estimation, valuation


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager"""
    # Startup
    create_db_and_tables()
    yield
    # Shutdown - add cleanup if needed


# FastAPI app initialization
app = FastAPI(
    title=getattr(settings, 'app_name', 'Valuation API'),
    description="API for item valuation and estimation management",
    version=getattr(settings, 'version', '1.0.0'),
    lifespan=lifespan
)

# Include routers
app.include_router(info.router, tags=["info"])
app.include_router(valuation.router, tags=["valuation"])
app.include_router(estimation.router, prefix="/estimations", tags=["estimations"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=getattr(settings, 'host', '127.0.0.1'),
        port=getattr(settings, 'port', 8000),
        reload=getattr(settings, 'debug', False)
    )