from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, and_, or_

from models import Accommodation, Destination, ItineraryDay
from auth.models import User
from accommodation.schemas import AccommodationCreate, AccommodationUpdate, AccommodationFilter
from accommodation.exceptions import AccommodationException


def create_accommodation(db: Session, accommodation_data: AccommodationCreate, user: Optional[User] = None) -> Accommodation:
    """Create a new accommodation"""
    # Check if user is admin if authorization is needed
    if user and hasattr(user, 'role') and user.role != 'admin':
        raise AccommodationException.UNAUTHORIZED
    
    # Check if destination exists
    destination = db.query(Destination).filter(Destination.id == accommodation_data.destination_id).first()
    if not destination:
        raise AccommodationException.DESTINATION_NOT_FOUND
    
    # Check if accommodation already exists
    existing_accommodation = db.query(Accommodation).filter(
        func.lower(Accommodation.name) == func.lower(accommodation_data.name),
        Accommodation.destination_id == accommodation_data.destination_id
    ).first()
    
    if existing_accommodation:
        raise AccommodationException.ACCOMMODATION_ALREADY_EXISTS
    
    # Create new accommodation
    accommodation = Accommodation(
        name=accommodation_data.name,
        destination_id=accommodation_data.destination_id,
        type=accommodation_data.type,
        description=accommodation_data.description,
        address=accommodation_data.address,
        stars=accommodation_data.stars,
        price_category=accommodation_data.price_category,
        latitude=accommodation_data.latitude,
        longitude=accommodation_data.longitude,
        amenities=accommodation_data.amenities,
        image_url=accommodation_data.image_url
    )
    
    db.add(accommodation)
    db.commit()
    db.refresh(accommodation)
    return accommodation


def get_accommodation(db: Session, accommodation_id: int) -> Accommodation:
    """Get an accommodation by ID"""
    accommodation = db.query(Accommodation).filter(Accommodation.id == accommodation_id).first()
    if not accommodation:
        raise AccommodationException.ACCOMMODATION_NOT_FOUND
    return accommodation


def get_accommodations(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    filters: Optional[AccommodationFilter] = None
) -> List[Accommodation]:
    """Get a list of accommodations with optional filtering"""
    query = db.query(Accommodation)
    
    # Apply filters if provided
    if filters:
        if filters.destination_id:
            query = query.filter(Accommodation.destination_id == filters.destination_id)
        
        if filters.type:
            query = query.filter(Accommodation.type == filters.type)
        
        if filters.min_stars is not None:
            query = query.filter(Accommodation.stars >= filters.min_stars)
        
        if filters.max_stars is not None:
            query = query.filter(Accommodation.stars <= filters.max_stars)
        
        if filters.min_price_category is not None:
            query = query.filter(Accommodation.price_category >= filters.min_price_category)
        
        if filters.max_price_category is not None:
            query = query.filter(Accommodation.price_category <= filters.max_price_category)
        
        if filters.search:
            search_term = f"%{filters.search.lower()}%"
            query = query.filter(
                or_(
                    func.lower(Accommodation.name).like(search_term),
                    func.lower(Accommodation.description).like(search_term),
                    func.lower(Accommodation.address).like(search_term)
                )
            )
    
    # Apply pagination
    accommodations = query.offset(skip).limit(limit).all()
    return accommodations


def update_accommodation(
    db: Session, 
    accommodation_id: int, 
    accommodation_data: AccommodationUpdate, 
    user: Optional[User] = None
) -> Accommodation:
    """Update an existing accommodation"""
    # Check if user is admin if authorization is needed
    if user and hasattr(User, 'role') and user.role != 'admin':
        raise AccommodationException.UNAUTHORIZED
    
    accommodation = get_accommodation(db, accommodation_id)
    
    # Validate destination if provided
    if accommodation_data.destination_id is not None:
        destination = db.query(Destination).filter(Destination.id == accommodation_data.destination_id).first()
        if not destination:
            raise AccommodationException.DESTINATION_NOT_FOUND
    
    # Update accommodation fields if provided
    if accommodation_data.name is not None:
        accommodation.name = accommodation_data.name
    
    if accommodation_data.destination_id is not None:
        accommodation.destination_id = accommodation_data.destination_id
    
    if accommodation_data.type is not None:
        accommodation.type = accommodation_data.type
    
    if accommodation_data.description is not None:
        accommodation.description = accommodation_data.description
    
    if accommodation_data.address is not None:
        accommodation.address = accommodation_data.address
    
    if accommodation_data.stars is not None:
        accommodation.stars = accommodation_data.stars
    
    if accommodation_data.price_category is not None:
        accommodation.price_category = accommodation_data.price_category
    
    if accommodation_data.latitude is not None:
        accommodation.latitude = accommodation_data.latitude
    
    if accommodation_data.longitude is not None:
        accommodation.longitude = accommodation_data.longitude
    
    if accommodation_data.amenities is not None:
        accommodation.amenities = accommodation_data.amenities
    
    if accommodation_data.image_url is not None:
        accommodation.image_url = accommodation_data.image_url
    
    try:
        db.commit()
        db.refresh(accommodation)
        return accommodation
    except IntegrityError:
        db.rollback()
        raise AccommodationException.ACCOMMODATION_ALREADY_EXISTS


def delete_accommodation(db: Session, accommodation_id: int, user: Optional[User] = None) -> bool:
    """Delete an accommodation"""
    # Check if user is admin if authorization is needed
    if user and hasattr(User, 'role') and user.role != 'admin':
        raise AccommodationException.UNAUTHORIZED
    
    accommodation = get_accommodation(db, accommodation_id)
    
    # Check if accommodation is referenced by any itinerary days
    associated_days = db.query(ItineraryDay)\
        .join(ItineraryDay.accommodations)\
        .filter(Accommodation.id == accommodation_id)\
        .first()
        
    if associated_days:
        raise AccommodationException.ACCOMMODATION_IN_USE
    
    db.delete(accommodation)
    db.commit()
    return True