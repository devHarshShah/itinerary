from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any, List
from enum import Enum

from src.models import ActivityCategory


class ActivityBase(BaseModel):
    name: str
    destination_id: int
    category: ActivityCategory
    description: Optional[str] = None
    duration_hours: float
    price_range: Optional[str] = None
    is_must_see: bool = False
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    image_url: Optional[str] = None
    
    @field_validator('duration_hours')
    @classmethod
    def validate_duration(cls, v):
        if v <= 0:
            raise ValueError('Duration hours must be positive')
        return v


class ActivityCreate(ActivityBase):
    pass


class ActivityUpdate(BaseModel):
    name: Optional[str] = None
    destination_id: Optional[int] = None
    category: Optional[ActivityCategory] = None
    description: Optional[str] = None
    duration_hours: Optional[float] = None
    price_range: Optional[str] = None
    is_must_see: Optional[bool] = None
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    image_url: Optional[str] = None
    
    @field_validator('duration_hours')
    @classmethod
    def validate_duration(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Duration hours must be positive')
        return v


class ActivityFilter(BaseModel):
    destination_id: Optional[int] = None
    category: Optional[ActivityCategory] = None
    is_must_see: Optional[bool] = None
    max_duration: Optional[float] = None
    min_duration: Optional[float] = None
    search: Optional[str] = None


class ActivityResponse(ActivityBase):
    id: int
    
    class Config:
        from_attributes = True