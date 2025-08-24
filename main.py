from contextlib import asynccontextmanager
from typing import Optional
from datetime import datetime, timezone

from fastapi import FastAPI, Query, HTTPException, Depends
from sqlmodel import Field, Session, SQLModel, create_engine, select
from pydantic import BaseModel

from internal.open_ai import valuate_item
from internal.misc import is_valid_url
from config import settings



# Models
class Estimation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), 
        nullable=False
    )
    title: str = Field(nullable=False)
    max_value: int = Field(nullable=False)
    min_value: int = Field(nullable=False)
    url: str = Field(nullable=False)


class EstimationResponse(BaseModel):
    """Response model for estimation endpoints"""
    id: int
    title: str
    min_value: int
    max_value: int
    created_at: datetime
    url: str 


class ValuationResponse(BaseModel):
    """Response model for valuation endpoint"""
    valuation: dict
    title: str


# Database setup
sqlite_file_name = "sqlite.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# Configure engine with connection pooling and optimizations
engine = create_engine(
    sqlite_url, 
    echo=settings.debug if hasattr(settings, 'debug') else False,
    connect_args={"check_same_thread": False}  # For SQLite threading
)

# Drop all tables
# SQLModel.metadata.drop_all(engine)

# # Recreate all tables with new columns
# SQLModel.metadata.create_all(engine)
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager"""
    # Startup
    create_db_and_tables()
    yield
    # Shutdown - add cleanup if needed


def create_db_and_tables():
    """Initialize database tables"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Dependency to get database session"""
    with Session(engine) as session:
        yield session


def create_estimation(
    session: Session, 
    title: str, 
    min_value: int, 
    max_value: int,
    url: str 
) -> Estimation:
    """Create a new estimation record"""
    estimation = Estimation(
        title=title, 
        max_value=max_value, 
        min_value=min_value,
        url=url
    )
    session.add(estimation)
    session.commit()
    session.refresh(estimation)
    return estimation


# FastAPI app with lifespan
app = FastAPI(
    title=settings.app_name if hasattr(settings, 'app_name') else "Valuation API",
    lifespan=lifespan
)


@app.get("/info")
async def info():
    """Get application information"""
    return {
        "app_name": getattr(settings, 'app_name', 'Valuation API'),
        "version": getattr(settings, 'version', '1.0.0')
    }


@app.get("/estimate", response_model=ValuationResponse)
async def get_gpt_data(
    image_url: str = Query(..., description="Image URL"),
    session: Session = Depends(get_session)
) -> ValuationResponse:
    """Get valuation data for an image URL"""
    if not is_valid_url(image_url):
        raise HTTPException(
            status_code=400, 
            detail="Invalid URL format provided"
        )
    
    try:
        response = valuate_item(image_url)
        
        # Handle different response types
        if response is None:
            raise HTTPException(
                status_code=502,
                detail="Valuation service returned empty response"
            )
        
        # If response is a string, try to parse it as JSON
        if isinstance(response, str):
            if not response.strip():
                raise HTTPException(
                    status_code=502,
                    detail="Valuation service returned empty string"
                )
            try:
                import json
                response = json.loads(response)
            except json.JSONDecodeError as e:
                raise HTTPException(
                    status_code=502,
                    detail=f"Invalid JSON response from valuation service: {str(e)}"
                )
        
        # Ensure response is a dictionary
        if not isinstance(response, dict):
            raise HTTPException(
                status_code=502,
                detail=f"Expected dict response, got {type(response)}: {response}"
            )
        
        # Validate response structure with detailed error messages
        required_fields = ["description", "min_value", "max_value"]
        missing_fields = [field for field in required_fields if field not in response]
        
        if missing_fields:
            raise HTTPException(
                status_code=502,
                detail=f"Missing required fields in valuation response: {missing_fields}. "
                       f"Available fields: {list(response.keys())}"
            )
        
        # Validate field types and values
        try:
            description = str(response["description"])
            min_value = int(response["min_value"])
            max_value = int(response["max_value"])
            
            if min_value < 0 or max_value < 0:
                raise ValueError("Values cannot be negative")
            
            if min_value > max_value:
                raise ValueError("Min value cannot be greater than max value")
                
        except (ValueError, TypeError) as e:
            raise HTTPException(
                status_code=502,
                detail=f"Invalid data types in valuation response: {str(e)}"
            )
        
        # Create estimation record
        estimation = create_estimation(
            session=session,
            title=description,
            min_value=min_value,
            max_value=max_value, 
            url=image_url
        )
        
        return ValuationResponse(
            valuation=response,
            title=description
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # Log the full error for debugging
        import traceback
        print(f"Unexpected error in get_gpt_data: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        
        raise HTTPException(
            status_code=500,
            detail=f"Error processing valuation request: {str(e)}"
        )


@app.get("/estimations", response_model=list[EstimationResponse])
async def get_estimations(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    session: Session = Depends(get_session)
) -> list[EstimationResponse]:
    """Get list of estimations with pagination"""
    statement = select(Estimation).offset(skip).limit(limit).order_by(Estimation.created_at.desc())
    estimations = session.exec(statement).all()
    
    return [
        EstimationResponse(
            id=est.id,
            title=est.title,
            min_value=est.min_value,
            max_value=est.max_value,
            created_at=est.created_at
        )
        for est in estimations
    ]


@app.get("/estimations/{estimation_id}", response_model=EstimationResponse)
async def get_estimation(
    estimation_id: int,
    session: Session = Depends(get_session)
) -> EstimationResponse:
    """Get a specific estimation by ID"""
    statement = select(Estimation).where(Estimation.id == estimation_id)
    estimation = session.exec(statement).first()
    
    if not estimation:
        raise HTTPException(
            status_code=404,
            detail=f"Estimation with id {estimation_id} not found"
        )
    
    return EstimationResponse(
        id=estimation.id,
        title=estimation.title,
        min_value=estimation.min_value,
        max_value=estimation.max_value,
        created_at=estimation.created_at
    )