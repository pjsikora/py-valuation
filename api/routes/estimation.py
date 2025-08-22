from typing import List
from fastapi import APIRouter, Query, HTTPException, Depends
from sqlmodel import Session

from schemas.estimation import EstimationResponse, EstimationCreate
from database.operations import (
    get_estimations,
    get_estimation_by_id,
    create_estimation,
    update_estimation,
    delete_estimation
)
from api.dependencies import get_session

router = APIRouter()


@router.get("/", response_model=List[EstimationResponse])
async def list_estimations(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    session: Session = Depends(get_session)
) -> List[EstimationResponse]:
    """Get list of estimations with pagination"""
    estimations = get_estimations(session, skip=skip, limit=limit)
    
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


@router.get("/{estimation_id}", response_model=EstimationResponse)
async def get_estimation(
    estimation_id: int,
    session: Session = Depends(get_session)
) -> EstimationResponse:
    """Get a specific estimation by ID"""
    estimation = get_estimation_by_id(session, estimation_id)
    
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


@router.post("/", response_model=EstimationResponse)
async def create_new_estimation(
    estimation_data: EstimationCreate,
    session: Session = Depends(get_session)
) -> EstimationResponse:
    """Create a new estimation"""
    # Validate min/max values
    if estimation_data.min_value > estimation_data.max_value:
        raise HTTPException(
            status_code=400,
            detail="Minimum value cannot be greater than maximum value"
        )
    
    estimation = create_estimation(
        session=session,
        title=estimation_data.title,
        min_value=estimation_data.min_value,
        max_value=estimation_data.max_value
    )
    
    return EstimationResponse(
        id=estimation.id,
        title=estimation.title,
        min_value=estimation.min_value,
        max_value=estimation.max_value,
        created_at=estimation.created_at
    )


@router.put("/{estimation_id}", response_model=EstimationResponse)
async def update_existing_estimation(
    estimation_id: int,
    estimation_data: EstimationCreate,
    session: Session = Depends(get_session)
) -> EstimationResponse:
    """Update an existing estimation"""
    # Validate min/max values
    if estimation_data.min_value > estimation_data.max_value:
        raise HTTPException(
            status_code=400,
            detail="Minimum value cannot be greater than maximum value"
        )
    
    estimation = update_estimation(
        session=session,
        estimation_id=estimation_id,
        title=estimation_data.title,
        min_value=estimation_data.min_value,
        max_value=estimation_data.max_value
    )
    
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


@router.delete("/{estimation_id}")
async def delete_existing_estimation(
    estimation_id: int,
    session: Session = Depends(get_session)
):
    """Delete an estimation"""
    deleted = delete_estimation(session, estimation_id)
    
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"Estimation with id {estimation_id} not found"
        )
    
    return {"message": f"Estimation {estimation_id} deleted successfully"}