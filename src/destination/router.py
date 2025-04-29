from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from auth.models import User
from auth.service import get_current_active_user, is_admin
from destination import service
from destination.schemas import DestinationCreate, DestinationUpdate, DestinationResponse

router = APIRouter(
    prefix="/destinations",
    tags=["destinations"],
)


@router.post("/", response_model=DestinationResponse, status_code=status.HTTP_201_CREATED)
def create_destination(
    destination_data: DestinationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin),
):
    """
    Create a new destination.
    
    Admin access is required.
    """
    return service.create_destination(db, destination_data, current_user)


@router.get("/", response_model=List[DestinationResponse])
def get_destinations(
    skip: int = 0,
    limit: int = 100,
    region: Optional[str] = None,
    country: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Get a list of destinations with optional filtering.
    
    Supports filtering by:
    - region
    - country
    - search term (searches in name, region, and description)
    """
    return service.get_destinations(db, skip, limit, region, country, search)


@router.get("/{destination_id}", response_model=DestinationResponse)
def get_destination(
    destination_id: int,
    db: Session = Depends(get_db),
):
    """
    Get detailed information about a specific destination by ID.
    """
    return service.get_destination(db, destination_id)


@router.put("/{destination_id}", response_model=DestinationResponse)
def update_destination(
    destination_id: int,
    destination_data: DestinationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin),
):
    """
    Update an existing destination.
    
    Admin access is required.
    """
    return service.update_destination(db, destination_id, destination_data, current_user)


@router.patch("/{destination_id}", response_model=DestinationResponse)
def partial_update_destination(
    destination_id: int,
    destination_data: DestinationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin),
):
    """
    Partially update an existing destination.
    
    This is an alias for the PUT endpoint for clients that prefer PATCH semantics.
    Admin access is required.
    """
    return service.update_destination(db, destination_id, destination_data, current_user)


@router.delete("/{destination_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_destination(
    destination_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin),
):
    """
    Delete a destination.
    
    This operation cannot be performed if the destination is referenced by any itineraries.
    Admin access is required.
    """
    service.delete_destination(db, destination_id, current_user)
    return None
