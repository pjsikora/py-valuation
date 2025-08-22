from typing import Optional
from datetime import datetime, timezone
from sqlmodel import Field, SQLModel


class Estimation(SQLModel, table=True):
    """Database model for item estimations"""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), 
        nullable=False,
        description="When the estimation was created"
    )
    title: str = Field(
        nullable=False,
        max_length=500,
        description="Description/title of the estimated item"
    )
    max_value: int = Field(
        nullable=False,
        ge=0,
        description="Maximum estimated value"
    )
    min_value: int = Field(
        nullable=False,
        ge=0,
        description="Minimum estimated value"
    )
    
    def __repr__(self):
        return f"<Estimation(id={self.id}, title='{self.title}', range={self.min_value}-{self.max_value})>"