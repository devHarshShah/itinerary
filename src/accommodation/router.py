from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

# Fix imports to use src prefix
from src.database import get_db
from src.accommodation import service
from src.accommodation.schemas import AccommodationCreate, AccommodationUpdate, AccommodationResponse, AccommodationFilter
from src.models import AccommodationType
from src.auth.service import get_current_active_user, is_admin
from src.auth.models import User

router = APIRouter(
    prefix="/accommodations",
    tags=["accommodations"],
)


@router.post("/", response_model=AccommodationResponse, status_code=status.HTTP_201_CREATED)
def create_accommodation(
    accommodation_data: AccommodationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin),
):
    """
    Create a new accommodation.
    
    Admin access is required.
    """
    return service.create_accommodation(db, accommodation_data, current_user)


@router.get("/", response_model=List[AccommodationResponse])
def get_accommodations(
    skip: int = 0,
    limit: int = 100,
    destination_id: Optional[int] = None,
    type: Optional[AccommodationType] = None,
    min_stars: Optional[float] = None,
    max_stars: Optional[float] = None,
    min_price_category: Optional[int] = None,
    max_price_category: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Get a list of accommodations with optional filtering.
    
    Supports filtering by:
    - destination_id
    - accommodation type
    - star rating range
    - price category range
    - search term (searches in name, description, and address)
    """
    filters = None
    if any([destination_id, type, min_stars is not None, max_stars is not None, 
           min_price_category is not None, max_price_category is not None, search]):
        filters = AccommodationFilter(
            destination_id=destination_id,
            type=type,
            min_stars=min_stars,
            max_stars=max_stars,
            min_price_category=min_price_category,
            max_price_category=max_price_category,
            search=search
        )
    
    return service.get_accommodations(db, skip, limit, filters)


@router.get("/{accommodation_id}", response_model=AccommodationResponse)
def get_accommodation(
    accommodation_id: int,
    db: Session = Depends(get_db),
):
    """
    Get detailed information about a specific accommodation by ID.
    """
    return service.get_accommodation(db, accommodation_id)


@router.put("/{accommodation_id}", response_model=AccommodationResponse)
def update_accommodation(
    accommodation_id: int,
    accommodation_data: AccommodationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin),
):
    """
    Update an existing accommodation.
    
    Admin access is required.
    """
    return service.update_accommodation(db, accommodation_id, accommodation_data, current_user)


@router.patch("/{accommodation_id}", response_model=AccommodationResponse)
def partial_update_accommodation(
    accommodation_id: int,
    accommodation_data: AccommodationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin),
):
    """
    Partially update an existing accommodation.
    
    This is an alias for the PUT endpoint for clients that prefer PATCH semantics.
    Admin access is required.
    """
    return service.update_accommodation(db, accommodation_id, accommodation_data, current_user)


@router.delete("/{accommodation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_accommodation(
    accommodation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin),
):
    """
    Delete an accommodation.
    
    This operation cannot be performed if the accommodation is referenced by any itineraries.
    Admin access is required.
    """
    service.delete_accommodation(db, accommodation_id, current_user)
    return None