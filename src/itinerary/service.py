from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from fastapi import HTTPException, status
from sqlalchemy import and_, or_
from sqlalchemy.sql import text
from pydantic import BaseModel

from src.models import Itinerary, ItineraryDay, Destination, Accommodation, Activity, Transfer
from src.auth.models import User
from src.itinerary.schemas import ItineraryCreate, ItineraryUpdate, ItineraryFilter, ItineraryDayCreate, ItineraryDayUpdate
from src.itinerary.exceptions import ItineraryException

# Define serializers for Accommodation, Activity, and Transfer
class AccommodationSerializer(BaseModel):
    id: int
    name: str
    type: str

    class Config:
        from_attributes = True

class ActivitySerializer(BaseModel):
    id: int
    name: str
    category: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    order: Optional[int] = None

    class Config:
        from_attributes = True

class TransferSerializer(BaseModel):
    id: int
    name: str
    type: str
    order: Optional[int] = None

    class Config:
        from_attributes = True

# Itinerary CRUD operations
def create_itinerary(db: Session, itinerary_data: ItineraryCreate, user: User = None) -> Itinerary:
    """Create a new itinerary with all its days, accommodations, activities, and transfers"""
    
    # Validate that the number of days matches the duration
    if len(itinerary_data.days) != itinerary_data.duration_nights + 1:
        raise ItineraryException.INVALID_DAYS_COUNT
    
    # Create the main itinerary
    itinerary = Itinerary(
        title=itinerary_data.title,
        duration_nights=itinerary_data.duration_nights,
        description=itinerary_data.description,
        preferences=itinerary_data.preferences,
        total_estimated_cost=itinerary_data.total_estimated_cost,
    )
    
    # If user is provided, associate itinerary with the user
    # This would require adding a user_id column to the Itinerary model
    if user and hasattr(Itinerary, 'user_id'):
        itinerary.user_id = user.id
    
    db.add(itinerary)
    db.flush()  # Flush to get the itinerary ID without committing
    
    # Create itinerary days
    for day_data in itinerary_data.days:
        # Validate destination exists
        destination = db.query(Destination).filter(Destination.id == day_data.main_destination_id).first()
        if not destination:
            raise ItineraryException.DESTINATION_NOT_FOUND
        
        # Create itinerary day
        day = ItineraryDay(
            itinerary_id=itinerary.id,
            day_number=day_data.day_number,
            main_destination_id=day_data.main_destination_id,
            description=day_data.description
        )
        db.add(day)
        db.flush()  # Flush to get the day ID
        
        # Add accommodations
        if day_data.accommodations:
            for accommodation_id in day_data.accommodations:
                accommodation = db.query(Accommodation).filter(Accommodation.id == accommodation_id).first()
                if not accommodation:
                    raise ItineraryException.ACCOMMODATION_NOT_FOUND
                day.accommodations.append(accommodation)
        
        # Add activities with time and order
        if day_data.activities:
            for activity_data in day_data.activities:
                activity = db.query(Activity).filter(Activity.id == activity_data["id"]).first()
                if not activity:
                    raise ItineraryException.ACTIVITY_NOT_FOUND
                
                # Add activity to day with additional data in the association table
                stmt = text(f"""
                INSERT INTO itinerary_activity (itinerary_day_id, activity_id, start_time, end_time, "order")
                VALUES ({day.id}, {activity.id}, 
                        {f"'{activity_data.get('start_time')}'" if activity_data.get('start_time') else 'NULL'}, 
                        {f"'{activity_data.get('end_time')}'" if activity_data.get('end_time') else 'NULL'}, 
                        {activity_data.get('order')})
                """)
                db.execute(stmt)
        
        # Add transfers with order
        if day_data.transfers:
            for transfer_data in day_data.transfers:
                transfer = db.query(Transfer).filter(Transfer.id == transfer_data["id"]).first()
                if not transfer:
                    raise ItineraryException.TRANSFER_NOT_FOUND
                
                # Add transfer to day with order in the association table
                stmt = text(f"""
                INSERT INTO itinerary_transfer (itinerary_day_id, transfer_id, "order")
                VALUES ({day.id}, {transfer.id}, {transfer_data.get('order')})
                """)
                db.execute(stmt)
    
    db.commit()
    db.refresh(itinerary)

    # Serialize the days with their related objects to avoid validation errors
    serialized_days = []
    for day in itinerary.days:
        serialized_day = {
            "id": day.id,
            "itinerary_id": day.itinerary_id,  # Add the itinerary_id field
            "day_number": day.day_number,
            "main_destination_id": day.main_destination_id,
            "description": day.description,
            "accommodations": [AccommodationSerializer.model_validate(acc).model_dump() for acc in day.accommodations],
            "activities": [ActivitySerializer.model_validate(act).model_dump() for act in day.activities],
            "transfers": [TransferSerializer.model_validate(tr).model_dump() for tr in day.transfers]
        }
        serialized_days.append(serialized_day)
    
    # Create a serialized version of the itinerary with the serialized days
    serialized_itinerary = {
        "id": itinerary.id,
        "uuid": itinerary.uuid,
        "title": itinerary.title,
        "duration_nights": itinerary.duration_nights,
        "description": itinerary.description,
        "preferences": itinerary.preferences,
        "is_recommended": itinerary.is_recommended,
        "total_estimated_cost": itinerary.total_estimated_cost,
        "created_at": itinerary.created_at,  # Add the created_at timestamp
        "updated_at": itinerary.updated_at,  # Add the updated_at timestamp
        "days": serialized_days
    }
    
    # Convert the serialized dictionary back to an Itinerary object
    from pydantic import create_model
    SerializedItinerary = create_model('SerializedItinerary', **{k: (type(v), ...) for k, v in serialized_itinerary.items()})
    return SerializedItinerary(**serialized_itinerary)


def get_itinerary(db: Session, itinerary_id: int):
    """Get an itinerary by ID with all related data"""
    itinerary = db.query(Itinerary).filter(Itinerary.id == itinerary_id).first()
    if not itinerary:
        raise ItineraryException.ITINERARY_NOT_FOUND
    
    # Serialize the days with their related objects to avoid validation errors
    serialized_days = []
    for day in itinerary.days:
        serialized_day = {
            "id": day.id,
            "itinerary_id": day.itinerary_id,
            "day_number": day.day_number,
            "main_destination_id": day.main_destination_id,
            "description": day.description,
            "accommodations": [AccommodationSerializer.model_validate(acc).model_dump() for acc in day.accommodations],
            "activities": [ActivitySerializer.model_validate(act).model_dump() for act in day.activities],
            "transfers": [TransferSerializer.model_validate(tr).model_dump() for tr in day.transfers]
        }
        serialized_days.append(serialized_day)
    
    # Create a serialized version of the itinerary with the serialized days
    serialized_itinerary = {
        "id": itinerary.id,
        "uuid": itinerary.uuid,
        "title": itinerary.title,
        "duration_nights": itinerary.duration_nights,
        "description": itinerary.description,
        "preferences": itinerary.preferences,
        "is_recommended": itinerary.is_recommended,
        "total_estimated_cost": itinerary.total_estimated_cost,
        "created_at": itinerary.created_at,
        "updated_at": itinerary.updated_at,
        "days": serialized_days
    }
    
    # Convert the serialized dictionary back to an Itinerary object
    from pydantic import create_model
    SerializedItinerary = create_model('SerializedItinerary', **{k: (type(v), ...) for k, v in serialized_itinerary.items()})
    return SerializedItinerary(**serialized_itinerary)


def get_itinerary_by_uuid(db: Session, uuid: str):
    """Get an itinerary by UUID with all related data"""
    itinerary = db.query(Itinerary).filter(Itinerary.uuid == uuid).first()
    if not itinerary:
        raise ItineraryException.ITINERARY_NOT_FOUND
    
    # Serialize the days with their related objects to avoid validation errors
    serialized_days = []
    for day in itinerary.days:
        serialized_day = {
            "id": day.id,
            "itinerary_id": day.itinerary_id,
            "day_number": day.day_number,
            "main_destination_id": day.main_destination_id,
            "description": day.description,
            "accommodations": [AccommodationSerializer.model_validate(acc).model_dump() for acc in day.accommodations],
            "activities": [ActivitySerializer.model_validate(act).model_dump() for act in day.activities],
            "transfers": [TransferSerializer.model_validate(tr).model_dump() for tr in day.transfers]
        }
        serialized_days.append(serialized_day)
    
    # Create a serialized version of the itinerary with the serialized days
    serialized_itinerary = {
        "id": itinerary.id,
        "uuid": itinerary.uuid,
        "title": itinerary.title,
        "duration_nights": itinerary.duration_nights,
        "description": itinerary.description,
        "preferences": itinerary.preferences,
        "is_recommended": itinerary.is_recommended,
        "total_estimated_cost": itinerary.total_estimated_cost,
        "created_at": itinerary.created_at,
        "updated_at": itinerary.updated_at,
        "days": serialized_days
    }
    
    # Convert the serialized dictionary back to an Itinerary object
    from pydantic import create_model
    SerializedItinerary = create_model('SerializedItinerary', **{k: (type(v), ...) for k, v in serialized_itinerary.items()})
    return SerializedItinerary(**serialized_itinerary)


def get_itineraries(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    filters: Optional[ItineraryFilter] = None,
    user_id: Optional[int] = None
):
    """Get a list of itineraries with optional filtering"""
    query = db.query(Itinerary)
    
    # Apply filters if provided
    if filters:
        if filters.is_recommended is not None:
            query = query.filter(Itinerary.is_recommended == filters.is_recommended)
        
        if filters.min_nights is not None:
            query = query.filter(Itinerary.duration_nights >= filters.min_nights)
        
        if filters.max_nights is not None:
            query = query.filter(Itinerary.duration_nights <= filters.max_nights)
        
        if filters.destination_id is not None:
            # Filter by destination - an itinerary includes a destination if any of its days has that destination
            query = query.join(ItineraryDay).filter(ItineraryDay.main_destination_id == filters.destination_id)
    
    # If user_id is provided, filter by user (assuming Itinerary has a user_id column)
    if user_id and hasattr(Itinerary, 'user_id'):
        query = query.filter(Itinerary.user_id == user_id)
    
    # Apply pagination
    itineraries = query.offset(skip).limit(limit).all()
    
    # Serialize the itineraries
    serialized_itineraries = []
    for itinerary in itineraries:
        serialized_itinerary = {
            "id": itinerary.id,
            "uuid": itinerary.uuid,
            "title": itinerary.title,
            "duration_nights": itinerary.duration_nights,
            "description": itinerary.description,
            "preferences": itinerary.preferences,
            "is_recommended": itinerary.is_recommended,
            "total_estimated_cost": itinerary.total_estimated_cost,
            "created_at": itinerary.created_at,
            "updated_at": itinerary.updated_at,
        }
        serialized_itineraries.append(serialized_itinerary)
    
    return serialized_itineraries


def update_itinerary(db: Session, itinerary_id: int, itinerary_data: ItineraryUpdate, user: Optional[User] = None):
    """Update an existing itinerary's basic information"""
    itinerary = db.query(Itinerary).filter(Itinerary.id == itinerary_id).first()
    if not itinerary:
        raise ItineraryException.ITINERARY_NOT_FOUND
    
    # If user is provided, check authorization (assuming Itinerary has a user_id column)
    if user and hasattr(Itinerary, 'user_id') and user.role != 'ADMIN':
        if itinerary.user_id != user.id:
            raise ItineraryException.UNAUTHORIZED
    
    # Update itinerary fields if provided
    if itinerary_data.title is not None:
        itinerary.title = itinerary_data.title
    
    if itinerary_data.description is not None:
        itinerary.description = itinerary_data.description
    
    if itinerary_data.is_recommended is not None:
        itinerary.is_recommended = itinerary_data.is_recommended
    
    if itinerary_data.preferences is not None:
        itinerary.preferences = itinerary_data.preferences
    
    if itinerary_data.total_estimated_cost is not None:
        itinerary.total_estimated_cost = itinerary_data.total_estimated_cost
    
    db.commit()
    db.refresh(itinerary)
    
    # Serialize the days with their related objects to avoid validation errors
    serialized_days = []
    for day in itinerary.days:
        serialized_day = {
            "id": day.id,
            "itinerary_id": day.itinerary_id,
            "day_number": day.day_number,
            "main_destination_id": day.main_destination_id,
            "description": day.description,
            "accommodations": [AccommodationSerializer.model_validate(acc).model_dump() for acc in day.accommodations],
            "activities": [ActivitySerializer.model_validate(act).model_dump() for act in day.activities],
            "transfers": [TransferSerializer.model_validate(tr).model_dump() for tr in day.transfers]
        }
        serialized_days.append(serialized_day)
    
    # Create a serialized version of the itinerary with the serialized days
    serialized_itinerary = {
        "id": itinerary.id,
        "uuid": itinerary.uuid,
        "title": itinerary.title,
        "duration_nights": itinerary.duration_nights,
        "description": itinerary.description,
        "preferences": itinerary.preferences,
        "is_recommended": itinerary.is_recommended,
        "total_estimated_cost": itinerary.total_estimated_cost,
        "created_at": itinerary.created_at,
        "updated_at": itinerary.updated_at,
        "days": serialized_days
    }
    
    # Convert the serialized dictionary back to an Itinerary object
    from pydantic import create_model
    SerializedItinerary = create_model('SerializedItinerary', **{k: (type(v), ...) for k, v in serialized_itinerary.items()})
    return SerializedItinerary(**serialized_itinerary)


def delete_itinerary(db: Session, itinerary_id: int, user: Optional[User] = None) -> bool:
    """Delete an itinerary and all associated data"""
    itinerary = get_itinerary(db, itinerary_id)
    
    # If user is provided, check authorization (assuming Itinerary has a user_id column)
    if user and hasattr(Itinerary, 'user_id') and user.role != 'ADMIN':
        if itinerary.user_id != user.id:
            raise ItineraryException.UNAUTHORIZED
    
    db.delete(itinerary)
    db.commit()
    return True


# Itinerary Day operations
def update_itinerary_day(
    db: Session, 
    itinerary_id: int, 
    day_number: int, 
    day_data: ItineraryDayUpdate, 
    user: Optional[User] = None
):
    """Update a specific day in an itinerary"""
    # Get the itinerary to ensure it exists and check authorization
    itinerary = db.query(Itinerary).filter(Itinerary.id == itinerary_id).first()
    if not itinerary:
        raise ItineraryException.ITINERARY_NOT_FOUND
    
    # If user is provided, check authorization (assuming Itinerary has a user_id column)
    if user and hasattr(Itinerary, 'user_id') and user.role != 'ADMIN':
        if itinerary.user_id != user.id:
            raise ItineraryException.UNAUTHORIZED
    
    # Get the day to update
    day = db.query(ItineraryDay).filter(
        ItineraryDay.itinerary_id == itinerary_id,
        ItineraryDay.day_number == day_number
    ).first()
    
    if not day:
        raise ItineraryException.INVALID_DAY_NUMBER
    
    # Update main destination if provided
    if day_data.main_destination_id is not None:
        # Validate destination exists
        destination = db.query(Destination).filter(Destination.id == day_data.main_destination_id).first()
        if not destination:
            raise ItineraryException.DESTINATION_NOT_FOUND
        day.main_destination_id = day_data.main_destination_id
    
    # Update description if provided
    if day_data.description is not None:
        day.description = day_data.description
    
    # Update accommodations if provided
    if day_data.accommodations is not None:
        # Clear existing accommodations
        day.accommodations = []
        
        # Add new accommodations
        for accommodation_id in day_data.accommodations:
            accommodation = db.query(Accommodation).filter(Accommodation.id == accommodation_id).first()
            if not accommodation:
                raise ItineraryException.ACCOMMODATION_NOT_FOUND
            day.accommodations.append(accommodation)
    
    # Update activities if provided
    if day_data.activities is not None:
        # Clear existing activities (need to delete from the association table)
        db.execute(f"DELETE FROM itinerary_activity WHERE itinerary_day_id = {day.id}")
        
        # Add new activities
        for activity_data in day_data.activities:
            activity = db.query(Activity).filter(Activity.id == activity_data["id"]).first()
            if not activity:
                raise ItineraryException.ACTIVITY_NOT_FOUND
            
            # Add activity to day with additional data in the association table
            stmt = text(f"""
            INSERT INTO itinerary_activity (itinerary_day_id, activity_id, start_time, end_time, "order")
            VALUES ({day.id}, {activity.id}, 
                    {f"'{activity_data.get('start_time')}'" if activity_data.get('start_time') else 'NULL'}, 
                    {f"'{activity_data.get('end_time')}'" if activity_data.get('end_time') else 'NULL'}, 
                    {activity_data.get('order')})
            """)
            db.execute(stmt)
    
    # Update transfers if provided
    if day_data.transfers is not None:
        # Clear existing transfers (need to delete from the association table)
        db.execute(f"DELETE FROM itinerary_transfer WHERE itinerary_day_id = {day.id}")
        
        # Add new transfers
        for transfer_data in day_data.transfers:
            transfer = db.query(Transfer).filter(Transfer.id == transfer_data["id"]).first()
            if not transfer:
                raise ItineraryException.TRANSFER_NOT_FOUND
            
            # Add transfer to day with order in the association table
            stmt = text(f"""
            INSERT INTO itinerary_transfer (itinerary_day_id, transfer_id, "order")
            VALUES ({day.id}, {transfer.id}, {transfer_data.get('order')})
            """)
            db.execute(stmt)
    
    db.commit()
    db.refresh(day)
    
    # Serialize the updated day with their related objects
    serialized_day = {
        "id": day.id,
        "itinerary_id": day.itinerary_id,
        "day_number": day.day_number,
        "main_destination_id": day.main_destination_id,
        "description": day.description,
        "accommodations": [AccommodationSerializer.model_validate(acc).model_dump() for acc in day.accommodations],
        "activities": [ActivitySerializer.model_validate(act).model_dump() for act in day.activities],
        "transfers": [TransferSerializer.model_validate(tr).model_dump() for tr in day.transfers]
    }
    
    return serialized_day


def add_itinerary_day(
    db: Session, 
    itinerary_id: int, 
    day_data: ItineraryDayCreate, 
    user: Optional[User] = None
):
    """Add a new day to an existing itinerary"""
    # Get the itinerary to ensure it exists and check authorization
    itinerary = db.query(Itinerary).filter(Itinerary.id == itinerary_id).first()
    if not itinerary:
        raise ItineraryException.ITINERARY_NOT_FOUND
    
    # If user is provided, check authorization (assuming Itinerary has a user_id column)
    if user and hasattr(Itinerary, 'user_id') and user.role != 'ADMIN':
        if itinerary.user_id != user.id:
            raise ItineraryException.UNAUTHORIZED
    
    # Check if day number is valid
    existing_day = db.query(ItineraryDay).filter(
        ItineraryDay.itinerary_id == itinerary_id,
        ItineraryDay.day_number == day_data.day_number
    ).first()
    
    if existing_day:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Day {day_data.day_number} already exists for this itinerary"
        )
    
    # Validate destination exists
    destination = db.query(Destination).filter(Destination.id == day_data.main_destination_id).first()
    if not destination:
        raise ItineraryException.DESTINATION_NOT_FOUND
    
    # Create itinerary day
    day = ItineraryDay(
        itinerary_id=itinerary.id,
        day_number=day_data.day_number,
        main_destination_id=day_data.main_destination_id,
        description=day_data.description
    )
    db.add(day)
    db.flush()  # Flush to get the day ID
    
    # Add accommodations
    if day_data.accommodations:
        for accommodation_id in day_data.accommodations:
            accommodation = db.query(Accommodation).filter(Accommodation.id == accommodation_id).first()
            if not accommodation:
                raise ItineraryException.ACCOMMODATION_NOT_FOUND
            day.accommodations.append(accommodation)
    
    # Add activities with time and order
    if day_data.activities:
        for activity_data in day_data.activities:
            activity = db.query(Activity).filter(Activity.id == activity_data["id"]).first()
            if not activity:
                raise ItineraryException.ACTIVITY_NOT_FOUND
            
            # Add activity to day with additional data in the association table
            stmt = text(f"""
            INSERT INTO itinerary_activity (itinerary_day_id, activity_id, start_time, end_time, "order")
            VALUES ({day.id}, {activity.id}, 
                    {f"'{activity_data.get('start_time')}'" if activity_data.get('start_time') else 'NULL'}, 
                    {f"'{activity_data.get('end_time')}'" if activity_data.get('end_time') else 'NULL'}, 
                    {activity_data.get('order')})
            """)
            db.execute(stmt)
    
    # Add transfers with order
    if day_data.transfers:
        for transfer_data in day_data.transfers:
            transfer = db.query(Transfer).filter(Transfer.id == transfer_data["id"]).first()
            if not transfer:
                raise ItineraryException.TRANSFER_NOT_FOUND
            
            # Add transfer to day with order in the association table
            stmt = text(f"""
            INSERT INTO itinerary_transfer (itinerary_day_id, transfer_id, "order")
            VALUES ({day.id}, {transfer.id}, {transfer_data.get('order')})
            """)
            db.execute(stmt)
    
    # Update itinerary duration if needed
    if day_data.day_number > itinerary.duration_nights + 1:
        itinerary.duration_nights = day_data.day_number - 1
        db.flush()
    
    db.commit()
    db.refresh(day)
    
    # Serialize the day with its related objects
    serialized_day = {
        "id": day.id,
        "itinerary_id": day.itinerary_id,
        "day_number": day.day_number,
        "main_destination_id": day.main_destination_id,
        "description": day.description,
        "accommodations": [AccommodationSerializer.model_validate(acc).model_dump() for acc in day.accommodations],
        "activities": [ActivitySerializer.model_validate(act).model_dump() for act in day.activities],
        "transfers": [TransferSerializer.model_validate(tr).model_dump() for tr in day.transfers]
    }
    
    return serialized_day


def delete_itinerary_day(
    db: Session, 
    itinerary_id: int, 
    day_number: int, 
    user: Optional[User] = None
) -> bool:
    """Delete a specific day from an itinerary"""
    # Get the itinerary to ensure it exists and check authorization
    itinerary = get_itinerary(db, itinerary_id)
    
    # If user is provided, check authorization (assuming Itinerary has a user_id column)
    if user and hasattr(Itinerary, 'user_id') and user.role != 'ADMIN':
        if itinerary.user_id != user.id:
            raise ItineraryException.UNAUTHORIZED
    
    # Get the day to delete
    day = db.query(ItineraryDay).filter(
        ItineraryDay.itinerary_id == itinerary_id,
        ItineraryDay.day_number == day_number
    ).first()
    
    if not day:
        raise ItineraryException.INVALID_DAY_NUMBER
    
    # Delete the day
    db.delete(day)
    
    # Update day numbers for all days after the deleted day
    days_to_update = db.query(ItineraryDay).filter(
        ItineraryDay.itinerary_id == itinerary_id,
        ItineraryDay.day_number > day_number
    ).all()
    
    for update_day in days_to_update:
        update_day.day_number -= 1
    
    # Update itinerary duration
    itinerary.duration_nights -= 1
    
    db.commit()
    return True