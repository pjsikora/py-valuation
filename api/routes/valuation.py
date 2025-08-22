import json
import traceback
from fastapi import APIRouter, Query, HTTPException, Depends
from sqlmodel import Session

from schemas.estimation import ValuationResponse
from database.operations import create_estimation
from api.dependencies import get_session
from internal.open_ai import valuate_item
from internal.misc import is_valid_url

router = APIRouter()


@router.get("/estimate", response_model=ValuationResponse)
async def get_valuation_estimate(
    image_url: str = Query(..., description="Image URL to valuate"),
    session: Session = Depends(get_session)
) -> ValuationResponse:
    """Get valuation data for an image URL and save as estimation"""
    if not is_valid_url(image_url):
        raise HTTPException(
            status_code=400,
            detail="Invalid URL format provided"
        )
    
    try:
        # Get valuation from external service with detailed logging
        print(f"Calling valuate_item with URL: {image_url}")
        response = valuate_item(image_url)
        print(f"Raw response from valuate_item: {response}")
        print(f"Response type: {type(response)}")
        
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
            max_value=max_value
        )
        
        return ValuationResponse(
            valuation=response,
            title=description
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # Log the full error for debugging
        print(f"Unexpected error in get_valuation_estimate: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        
        raise HTTPException(
            status_code=500,
            detail=f"Error processing valuation request: {str(e)}"
        )


@router.get("/debug-valuate")
async def debug_valuate(image_url: str = Query(..., description="Image URL for debugging")):
    """Debug endpoint to test valuate_item function"""
    try:
        result = valuate_item(image_url)
        return {
            "result": result,
            "type": str(type(result)),
            "is_none": result is None,
            "is_empty": result == "" if result is not None else False,
            "length": len(str(result)) if result is not None else 0
        }
    except Exception as e:
        return {
            "error": str(e),
            "error_type": str(type(e)),
            "traceback": traceback.format_exc()
        }