from datetime import datetime
from pydantic import BaseModel, Field


class EstimationResponse(BaseModel):
    """Response model for estimation endpoints"""
    
    id: int = Field(description="Unique estimation ID")
    title: str = Field(description="Item description/title")
    min_value: int = Field(ge=0, description="Minimum estimated value")
    max_value: int = Field(ge=0, description="Maximum estimated value") 
    created_at: datetime = Field(description="Creation timestamp")
    
    class Config:
        from_attributes = True


class ValuationResponse(BaseModel):
    """Response model for valuation endpoint"""
    
    valuation: dict = Field(description="Raw valuation data from AI service")
    title: str = Field(description="Item title/description")


class EstimationCreate(BaseModel):
    """Schema for creating new estimations"""
    
    title: str = Field(min_length=1, max_length=500, description="Item description")
    min_value: int = Field(ge=0, description="Minimum estimated value")
    max_value: int = Field(ge=0, description="Maximum estimated value")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Vintage watch",
                "min_value": 100,
                "max_value": 500
            }
        }