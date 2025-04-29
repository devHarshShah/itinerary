from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from auth.models import User
from auth.service import get_current_active_user, is_admin
from itinerary import service
from itinerary.schemas import (
    ItineraryCreate,
    ItineraryUpdate,
    ItineraryResponse,
    ItineraryDetailResponse,
    ItineraryFilter,
    ItineraryDayCreate,
    ItineraryDayUpdate
)

router = APIRouter(
    prefix="/itineraries",
    tags=["itineraries"],
)


# Itinerary Creation Endpoint
@router.post("/", response_model=ItineraryDetailResponse, status_code=status.HTTP_201_CREATED)
def create_itinerary(
    itinerary_data: ItineraryCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user),
):
    """
    Create a new itinerary with all its days, accommodations, activities, and transfers.
    
    This endpoint handles the complete creation of a travel plan with all associated elements.
    """
    return service.create_itinerary(db, itinerary_data, current_user)


# Itinerary Retrieval Endpoints
@router.get("/", response_model=List[ItineraryResponse])
def get_itineraries(
    skip: int = 0,
    limit: int = 100,
    destination_id: Optional[int] = None,
    min_nights: Optional[int] = None,
    max_nights: Optional[int] = None,
    is_recommended: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user),
):
    """
    Get a list of itineraries with optional filtering.
    
    Supports filtering by:
    - destination
    - minimum/maximum nights
    - recommended status
    """
    filters = None
    if any([destination_id, min_nights, max_nights, is_recommended is not None]):
        filters = ItineraryFilter(
            destination_id=destination_id,
            min_nights=min_nights,
            max_nights=max_nights,
            is_recommended=is_recommended
        )
    
    # Get user_id for filtering if the user is not an admin
    user_id = None
    if current_user and hasattr(User, 'role') and current_user.role != 'ADMIN' and hasattr(User, 'id'):
        user_id = current_user.id
    
    return service.get_itineraries(db, skip, limit, filters, user_id)


@router.get("/recommended", response_model=List[ItineraryResponse])
def get_recommended_itineraries(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    """
    Get a list of recommended itineraries.
    
    This is a convenience endpoint for featured itineraries.
    """
    filters = ItineraryFilter(is_recommended=True)
    return service.get_itineraries(db, skip, limit, filters)


@router.get("/{itinerary_id}", response_model=ItineraryDetailResponse)
def get_itinerary(
    itinerary_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user),
):
    """
    Get detailed information about a specific itinerary by ID.
    
    Returns the complete itinerary with all days, accommodations, activities, and transfers.
    """
    return service.get_itinerary(db, itinerary_id)


@router.get("/by-uuid/{uuid}", response_model=ItineraryDetailResponse)
def get_itinerary_by_uuid(
    uuid: str,
    db: Session = Depends(get_db),
):
    """
    Get detailed information about a specific itinerary by UUID.
    
    This endpoint is useful for public sharing of itineraries.
    """
    return service.get_itinerary_by_uuid(db, uuid)


# Itinerary Update Endpoints
@router.put("/{itinerary_id}", response_model=ItineraryDetailResponse)
def update_itinerary(
    itinerary_id: int,
    itinerary_data: ItineraryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Update an existing itinerary's basic information.
    
    This endpoint allows modifications to the main itinerary properties,
    but not to the associated days, accommodations, activities, or transfers.
    """
    return service.update_itinerary(db, itinerary_id, itinerary_data, current_user)


@router.patch("/{itinerary_id}", response_model=ItineraryDetailResponse)
def partial_update_itinerary(
    itinerary_id: int,
    itinerary_data: ItineraryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Partially update an existing itinerary.
    
    This is an alias for the PUT endpoint for clients that prefer PATCH semantics.
    """
    return service.update_itinerary(db, itinerary_id, itinerary_data, current_user)


# Itinerary Day Update Endpoints
@router.post("/{itinerary_id}/days", status_code=status.HTTP_201_CREATED)
def add_itinerary_day(
    itinerary_id: int,
    day_data: ItineraryDayCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Add a new day to an existing itinerary.
    
    This endpoint allows adding a complete day with accommodations, activities, and transfers.
    """
    return service.add_itinerary_day(db, itinerary_id, day_data, current_user)


@router.put("/{itinerary_id}/days/{day_number}")
def update_itinerary_day(
    itinerary_id: int,
    day_number: int,
    day_data: ItineraryDayUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Update a specific day in an itinerary.
    
    This endpoint allows modifications to a day's destination, accommodations, activities, and transfers.
    """
    return service.update_itinerary_day(db, itinerary_id, day_number, day_data, current_user)


@router.delete("/{itinerary_id}/days/{day_number}", status_code=status.HTTP_204_NO_CONTENT)
def delete_itinerary_day(
    itinerary_id: int,
    day_number: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Delete a specific day from an itinerary.
    
    This will also update the day numbers of all subsequent days and adjust the itinerary duration.
    """
    service.delete_itinerary_day(db, itinerary_id, day_number, current_user)
    return None


# Itinerary Deletion Endpoint
@router.delete("/{itinerary_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_itinerary(
    itinerary_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Delete an itinerary and all associated data.
    
    This operation cannot be undone.
    """
    service.delete_itinerary(db, itinerary_id, current_user)
    return None