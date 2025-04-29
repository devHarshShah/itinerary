from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, and_, or_

from src.models import Activity, Destination, ItineraryDay
from src.auth.models import User
from src.activity.schemas import ActivityCreate, ActivityUpdate, ActivityFilter
from src.activity.exceptions import ActivityException


def create_activity(db: Session, activity_data: ActivityCreate, user: Optional[User] = None) -> Activity:
    """Create a new activity"""
    # Check if user is admin if authorization is needed
    if user and hasattr(user, 'role') and user.role != 'admin':
        raise ActivityException.UNAUTHORIZED
    
    # Check if destination exists
    destination = db.query(Destination).filter(Destination.id == activity_data.destination_id).first()
    if not destination:
        raise ActivityException.DESTINATION_NOT_FOUND
    
    # Check if activity already exists
    existing_activity = db.query(Activity).filter(
        func.lower(Activity.name) == func.lower(activity_data.name),
        Activity.destination_id == activity_data.destination_id
    ).first()
    
    if existing_activity:
        raise ActivityException.ACTIVITY_ALREADY_EXISTS
    
    # Create new activity
    activity = Activity(
        name=activity_data.name,
        destination_id=activity_data.destination_id,
        category=activity_data.category,
        description=activity_data.description,
        duration_hours=activity_data.duration_hours,
        price_range=activity_data.price_range,
        is_must_see=activity_data.is_must_see,
        location=activity_data.location,
        latitude=activity_data.latitude,
        longitude=activity_data.longitude,
        image_url=activity_data.image_url
    )
    
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity


def get_activity(db: Session, activity_id: int) -> Activity:
    """Get an activity by ID"""
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise ActivityException.ACTIVITY_NOT_FOUND
    return activity


def get_activities(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    filters: Optional[ActivityFilter] = None
) -> List[Activity]:
    """Get a list of activities with optional filtering"""
    query = db.query(Activity)
    
    # Apply filters if provided
    if filters:
        if filters.destination_id:
            query = query.filter(Activity.destination_id == filters.destination_id)
        
        if filters.category:
            query = query.filter(Activity.category == filters.category)
        
        if filters.is_must_see is not None:
            query = query.filter(Activity.is_must_see == filters.is_must_see)
        
        if filters.min_duration is not None:
            query = query.filter(Activity.duration_hours >= filters.min_duration)
        
        if filters.max_duration is not None:
            query = query.filter(Activity.duration_hours <= filters.max_duration)
        
        if filters.search:
            search_term = f"%{filters.search.lower()}%"
            query = query.filter(
                or_(
                    func.lower(Activity.name).like(search_term),
                    func.lower(Activity.description).like(search_term),
                    func.lower(Activity.location).like(search_term)
                )
            )
    
    # Apply pagination
    activities = query.offset(skip).limit(limit).all()
    return activities


def update_activity(
    db: Session, 
    activity_id: int, 
    activity_data: ActivityUpdate, 
    user: Optional[User] = None
) -> Activity:
    """Update an existing activity"""
    # Check if user is admin if authorization is needed
    if user and hasattr(User, 'role') and user.role != 'admin':
        raise ActivityException.UNAUTHORIZED
    
    activity = get_activity(db, activity_id)
    
    # Validate destination if provided
    if activity_data.destination_id is not None:
        destination = db.query(Destination).filter(Destination.id == activity_data.destination_id).first()
        if not destination:
            raise ActivityException.DESTINATION_NOT_FOUND
    
    # Update activity fields if provided
    if activity_data.name is not None:
        activity.name = activity_data.name
    
    if activity_data.destination_id is not None:
        activity.destination_id = activity_data.destination_id
    
    if activity_data.category is not None:
        activity.category = activity_data.category
    
    if activity_data.description is not None:
        activity.description = activity_data.description
    
    if activity_data.duration_hours is not None:
        activity.duration_hours = activity_data.duration_hours
    
    if activity_data.price_range is not None:
        activity.price_range = activity_data.price_range
    
    if activity_data.is_must_see is not None:
        activity.is_must_see = activity_data.is_must_see
    
    if activity_data.location is not None:
        activity.location = activity_data.location
    
    if activity_data.latitude is not None:
        activity.latitude = activity_data.latitude
    
    if activity_data.longitude is not None:
        activity.longitude = activity_data.longitude
    
    if activity_data.image_url is not None:
        activity.image_url = activity_data.image_url
    
    try:
        db.commit()
        db.refresh(activity)
        return activity
    except IntegrityError:
        db.rollback()
        raise ActivityException.ACTIVITY_ALREADY_EXISTS


def delete_activity(db: Session, activity_id: int, user: Optional[User] = None) -> bool:
    """Delete an activity"""
    # Check if user is admin if authorization is needed
    if user and hasattr(User, 'role') and user.role != 'admin':
        raise ActivityException.UNAUTHORIZED
    
    activity = get_activity(db, activity_id)
    
    # Check if activity is referenced by any itinerary days
    # Need to check the many-to-many relationship through the association table
    associated_days = db.query(ItineraryDay)\
        .join(ItineraryDay.activities)\
        .filter(Activity.id == activity_id)\
        .first()
        
    if associated_days:
        raise ActivityException.ACTIVITY_IN_USE
    
    db.delete(activity)
    db.commit()
    return True