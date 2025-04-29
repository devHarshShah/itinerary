from pydantic import BaseModel, Field, UUID4, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime, time
from enum import Enum

from src.models import TransportType, AccommodationType, ActivityCategory


# ========== Base Schema Classes ==========

class DestinationBase(BaseModel):
    id: int


class AccommodationBase(BaseModel):
    id: int


class ActivityBase(BaseModel):
    id: int
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    order: int


class TransferBase(BaseModel):
    id: int
    order: int


# ========== Itinerary Day Schemas ==========

class ItineraryDayCreate(BaseModel):
    day_number: int
    main_destination_id: int
    description: Optional[str] = None
    accommodations: List[int] = []  # List of accommodation IDs
    activities: List[Dict[str, Any]] = []  # List of activities with time and order
    transfers: List[Dict[str, Any]] = []  # List of transfers with order


class ItineraryDayUpdate(BaseModel):
    main_destination_id: Optional[int] = None
    description: Optional[str] = None
    accommodations: Optional[List[int]] = None  # List of accommodation IDs
    activities: Optional[List[Dict[str, Any]]] = None  # List of activities with time and order
    transfers: Optional[List[Dict[str, Any]]] = None  # List of transfers with order


class ItineraryDayResponse(BaseModel):
    id: int
    itinerary_id: int
    day_number: int
    main_destination_id: int
    description: Optional[str] = None
    accommodations: List[Dict[str, Any]] = []
    activities: List[Dict[str, Any]] = []
    transfers: List[Dict[str, Any]] = []
    
    class Config:
        from_attributes = True


# ========== Itinerary Schemas ==========

class ItineraryCreate(BaseModel):
    title: str
    duration_nights: int
    description: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None
    total_estimated_cost: Optional[float] = None
    days: List[ItineraryDayCreate]
    
    @field_validator('duration_nights')
    @classmethod
    def validate_duration(cls, v):
        if v <= 0:
            raise ValueError('Duration must be at least 1 night')
        return v


class ItineraryUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_recommended: Optional[bool] = None
    preferences: Optional[Dict[str, Any]] = None
    total_estimated_cost: Optional[float] = None


class ItineraryFilter(BaseModel):
    destination_id: Optional[int] = None
    min_nights: Optional[int] = None
    max_nights: Optional[int] = None
    is_recommended: Optional[bool] = None


class ItineraryResponse(BaseModel):
    id: int
    title: str
    uuid: UUID4
    duration_nights: int
    is_recommended: bool
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    preferences: Optional[Dict[str, Any]] = None
    total_estimated_cost: Optional[float] = None
    
    class Config:
        from_attributes = True


class ItineraryDetailResponse(ItineraryResponse):
    days: List[ItineraryDayResponse] = []
    
    class Config:
        from_attributes = True