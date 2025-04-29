from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any, List
from enum import Enum

from src.models import TransportType


class TransferBase(BaseModel):
    name: str
    origin_id: int
    destination_id: int
    type: str  # Changed from TransportType to str to accept string values like "taxi"
    duration_hours: float
    description: Optional[str] = None
    price_category: Optional[int] = None  # Added price_category to match test data
    provider: Optional[str] = None  # Added provider to match test data
    additional_info: Optional[str] = None  # Added additional_info field
    contact_info: Optional[Dict[str, Any]] = None  # Added contact_info field
    
    @field_validator('duration_hours')
    @classmethod
    def validate_duration(cls, v):
        if v <= 0:
            raise ValueError('Duration hours must be positive')
        return v
    
    @field_validator('destination_id')
    @classmethod
    def validate_different_destinations(cls, v, values):
        if 'origin_id' in values.data and v == values.data['origin_id']:
            raise ValueError('Origin and destination must be different')
        return v


class TransferCreate(TransferBase):
    pass


class TransferUpdate(BaseModel):
    name: Optional[str] = None
    origin_id: Optional[int] = None
    destination_id: Optional[int] = None
    type: Optional[str] = None  # Changed from TransportType to str
    duration_hours: Optional[float] = None
    description: Optional[str] = None
    price_category: Optional[int] = None  # Added to match test data
    provider: Optional[str] = None  # Added to match test data
    additional_info: Optional[str] = None  # Added additional_info field
    contact_info: Optional[Dict[str, Any]] = None  # Added contact_info field
    
    @field_validator('duration_hours')
    @classmethod
    def validate_duration(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Duration hours must be positive')
        return v
    
    @field_validator('destination_id')
    @classmethod
    def validate_different_destinations(cls, v, values):
        if v is not None and 'origin_id' in values.data and v == values.data['origin_id']:
            raise ValueError('Origin and destination must be different')
        return v


class TransferFilter(BaseModel):
    origin_id: Optional[int] = None
    destination_id: Optional[int] = None
    type: Optional[TransportType] = None
    max_duration: Optional[float] = None
    min_duration: Optional[float] = None
    search: Optional[str] = None


class TransferResponse(TransferBase):
    id: int
    
    class Config:
        from_attributes = True