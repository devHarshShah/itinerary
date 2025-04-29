from pydantic import BaseModel, Field
from typing import Optional, List


class DestinationBase(BaseModel):
    name: str
    region: str
    country: str = "Thailand"
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    image_url: Optional[str] = None


class DestinationCreate(DestinationBase):
    pass


class DestinationUpdate(BaseModel):
    name: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    image_url: Optional[str] = None


class DestinationResponse(DestinationBase):
    id: int
    
    class Config:
        from_attributes = True
