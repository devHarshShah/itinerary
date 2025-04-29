from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func

from src.models import Destination, ItineraryDay
from src.auth.models import User
from src.destination.schemas import DestinationCreate, DestinationUpdate
from src.destination.exceptions import DestinationException


def create_destination(db: Session, destination_data: DestinationCreate, user: Optional[User] = None) -> Destination:
    """Create a new destination"""
    # Check if user is admin if authorization is needed
    if user and hasattr(user, 'role') and user.role != 'admin':
        raise DestinationException.UNAUTHORIZED
    
    # Check if destination already exists
    existing_destination = db.query(Destination).filter(
        func.lower(Destination.name) == func.lower(destination_data.name),
        func.lower(Destination.region) == func.lower(destination_data.region)
    ).first()
    
    if existing_destination:
        raise DestinationException.DESTINATION_ALREADY_EXISTS
    
    # Create new destination
    destination = Destination(
        name=destination_data.name,
        region=destination_data.region,
        country=destination_data.country,
        description=destination_data.description,
        latitude=destination_data.latitude,
        longitude=destination_data.longitude,
        image_url=destination_data.image_url
    )
    
    db.add(destination)
    db.commit()
    db.refresh(destination)
    return destination


def get_destination(db: Session, destination_id: int) -> Destination:
    """Get a destination by ID"""
    destination = db.query(Destination).filter(Destination.id == destination_id).first()
    if not destination:
        raise DestinationException.DESTINATION_NOT_FOUND
    return destination


def get_destinations(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    region: Optional[str] = None,
    country: Optional[str] = None,
    search: Optional[str] = None
) -> List[Destination]:
    """Get a list of destinations with optional filtering"""
    query = db.query(Destination)
    
    # Apply filters if provided
    if region:
        query = query.filter(func.lower(Destination.region) == func.lower(region))
    
    if country:
        query = query.filter(func.lower(Destination.country) == func.lower(country))
    
    if search:
        search_term = f"%{search.lower()}%"
        query = query.filter(
            func.lower(Destination.name).like(search_term) | 
            func.lower(Destination.region).like(search_term) |
            func.lower(Destination.description).like(search_term)
        )
    
    # Apply pagination
    destinations = query.offset(skip).limit(limit).all()
    return destinations


def update_destination(
    db: Session, 
    destination_id: int, 
    destination_data: DestinationUpdate, 
    user: Optional[User] = None
) -> Destination:
    """Update an existing destination"""
    # Check if user is admin if authorization is needed
    if user and hasattr(User, 'role') and user.role != 'admin':
        raise DestinationException.UNAUTHORIZED
    
    destination = get_destination(db, destination_id)
    
    # Update destination fields if provided
    if destination_data.name is not None:
        destination.name = destination_data.name
    
    if destination_data.region is not None:
        destination.region = destination_data.region
    
    if destination_data.country is not None:
        destination.country = destination_data.country
    
    if destination_data.description is not None:
        destination.description = destination_data.description
    
    if destination_data.latitude is not None:
        destination.latitude = destination_data.latitude
    
    if destination_data.longitude is not None:
        destination.longitude = destination_data.longitude
    
    if destination_data.image_url is not None:
        destination.image_url = destination_data.image_url
    
    try:
        db.commit()
        db.refresh(destination)
        return destination
    except IntegrityError:
        db.rollback()
        raise DestinationException.DESTINATION_ALREADY_EXISTS


def delete_destination(db: Session, destination_id: int, user: Optional[User] = None) -> bool:
    """Delete a destination"""
    # Check if user is admin if authorization is needed
    if user and hasattr(User, 'role') and user.role != 'admin':
        raise DestinationException.UNAUTHORIZED
    
    destination = get_destination(db, destination_id)
    
    # Check if destination is referenced by any itinerary days
    is_used = db.query(ItineraryDay).filter(ItineraryDay.main_destination_id == destination_id).first()
    if is_used:
        raise DestinationException.DESTINATION_IN_USE
    
    db.delete(destination)
    db.commit()
    return True