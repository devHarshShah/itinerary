from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any, List
from enum import Enum

from src.models import AccommodationType


class AccommodationBase(BaseModel):
    name: str
    destination_id: int
    type: AccommodationType
    description: Optional[str] = None
    address: Optional[str] = None
    stars: Optional[float] = None
    price_category: int
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    amenities: Optional[Dict[str, Any]] = None
    image_url: Optional[str] = None
    
    @field_validator('stars')
    @classmethod
    def validate_stars(cls, v):
        if v is not None and (v < 0 or v > 5):
            raise ValueError('Stars must be between 0 and 5')
        return v
    
    @field_validator('price_category')
    @classmethod
    def validate_price_category(cls, v):
        if v < 1 or v > 5:
            raise ValueError('Price category must be between 1 and 5')
        return v


class AccommodationCreate(AccommodationBase):
    pass


class AccommodationUpdate(BaseModel):
    name: Optional[str] = None
    destination_id: Optional[int] = None
    type: Optional[AccommodationType] = None
    description: Optional[str] = None
    address: Optional[str] = None
    stars: Optional[float] = None
    price_category: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    amenities: Optional[Dict[str, Any]] = None
    image_url: Optional[str] = None
    
    @field_validator('stars')
    @classmethod
    def validate_stars(cls, v):
        if v is not None and (v < 0 or v > 5):
            raise ValueError('Stars must be between 0 and 5')
        return v
    
    @field_validator('price_category')
    @classmethod
    def validate_price_category(cls, v):
        if v is not None and (v < 1 or v > 5):
            raise ValueError('Price category must be between 1 and 5')
        return v


class AccommodationFilter(BaseModel):
    destination_id: Optional[int] = None
    type: Optional[AccommodationType] = None
    min_stars: Optional[float] = None
    max_stars: Optional[float] = None
    min_price_category: Optional[int] = None
    max_price_category: Optional[int] = None
    search: Optional[str] = None


class AccommodationResponse(AccommodationBase):
    id: int
    
    class Config:
        from_attributes = True