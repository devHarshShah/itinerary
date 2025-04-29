from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, and_, or_

from models import Transfer, Destination, ItineraryDay
from auth.models import User
from transfer.schemas import TransferCreate, TransferUpdate, TransferFilter
from transfer.exceptions import TransferException


def create_transfer(db: Session, transfer_data: TransferCreate, user: Optional[User] = None) -> Transfer:
    """Create a new transfer"""
    # Check if user is admin if authorization is needed
    if user and hasattr(user, 'role') and user.role != 'admin':
        raise TransferException.UNAUTHORIZED
    
    # Check if origin destination exists
    origin = db.query(Destination).filter(Destination.id == transfer_data.origin_id).first()
    if not origin:
        raise TransferException.DESTINATION_NOT_FOUND
    
    # Check if destination exists
    destination = db.query(Destination).filter(Destination.id == transfer_data.destination_id).first()
    if not destination:
        raise TransferException.DESTINATION_NOT_FOUND
    
    # Ensure origin and destination are different
    if transfer_data.origin_id == transfer_data.destination_id:
        raise TransferException.SAME_DESTINATIONS
    
    # Check if transfer already exists
    existing_transfer = db.query(Transfer).filter(
        func.lower(Transfer.name) == func.lower(transfer_data.name),
        Transfer.origin_id == transfer_data.origin_id,
        Transfer.destination_id == transfer_data.destination_id
    ).first()
    
    if existing_transfer:
        raise TransferException.TRANSFER_ALREADY_EXISTS
    
    # Create new transfer
    transfer = Transfer(
        name=transfer_data.name,
        origin_id=transfer_data.origin_id,
        destination_id=transfer_data.destination_id,
        type=transfer_data.type,
        duration_hours=transfer_data.duration_hours,
        description=transfer_data.description,
        price_range=transfer_data.price_range
    )
    
    db.add(transfer)
    db.commit()
    db.refresh(transfer)
    return transfer


def get_transfer(db: Session, transfer_id: int) -> Transfer:
    """Get a transfer by ID"""
    transfer = db.query(Transfer).filter(Transfer.id == transfer_id).first()
    if not transfer:
        raise TransferException.TRANSFER_NOT_FOUND
    return transfer


def get_transfers(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    filters: Optional[TransferFilter] = None
) -> List[Transfer]:
    """Get a list of transfers with optional filtering"""
    query = db.query(Transfer)
    
    # Apply filters if provided
    if filters:
        if filters.origin_id:
            query = query.filter(Transfer.origin_id == filters.origin_id)
        
        if filters.destination_id:
            query = query.filter(Transfer.destination_id == filters.destination_id)
        
        if filters.type:
            query = query.filter(Transfer.type == filters.type)
        
        if filters.min_duration is not None:
            query = query.filter(Transfer.duration_hours >= filters.min_duration)
        
        if filters.max_duration is not None:
            query = query.filter(Transfer.duration_hours <= filters.max_duration)
        
        if filters.search:
            search_term = f"%{filters.search.lower()}%"
            query = query.filter(
                or_(
                    func.lower(Transfer.name).like(search_term),
                    func.lower(Transfer.description).like(search_term)
                )
            )
    
    # Apply pagination
    transfers = query.offset(skip).limit(limit).all()
    return transfers


def update_transfer(
    db: Session, 
    transfer_id: int, 
    transfer_data: TransferUpdate, 
    user: Optional[User] = None
) -> Transfer:
    """Update an existing transfer"""
    # Check if user is admin if authorization is needed
    if user and hasattr(User, 'role') and user.role != 'admin':
        raise TransferException.UNAUTHORIZED
    
    transfer = get_transfer(db, transfer_id)
    
    # Validate origin if provided
    if transfer_data.origin_id is not None:
        origin = db.query(Destination).filter(Destination.id == transfer_data.origin_id).first()
        if not origin:
            raise TransferException.DESTINATION_NOT_FOUND
    
    # Validate destination if provided
    if transfer_data.destination_id is not None:
        destination = db.query(Destination).filter(Destination.id == transfer_data.destination_id).first()
        if not destination:
            raise TransferException.DESTINATION_NOT_FOUND
    
    # Ensure origin and destination are different if both provided
    new_origin_id = transfer_data.origin_id if transfer_data.origin_id is not None else transfer.origin_id
    new_destination_id = transfer_data.destination_id if transfer_data.destination_id is not None else transfer.destination_id
    
    if new_origin_id == new_destination_id:
        raise TransferException.SAME_DESTINATIONS
    
    # Update transfer fields if provided
    if transfer_data.name is not None:
        transfer.name = transfer_data.name
    
    if transfer_data.origin_id is not None:
        transfer.origin_id = transfer_data.origin_id
    
    if transfer_data.destination_id is not None:
        transfer.destination_id = transfer_data.destination_id
    
    if transfer_data.type is not None:
        transfer.type = transfer_data.type
    
    if transfer_data.duration_hours is not None:
        transfer.duration_hours = transfer_data.duration_hours
    
    if transfer_data.description is not None:
        transfer.description = transfer_data.description
    
    if transfer_data.price_range is not None:
        transfer.price_range = transfer_data.price_range
    
    try:
        db.commit()
        db.refresh(transfer)
        return transfer
    except IntegrityError:
        db.rollback()
        raise TransferException.TRANSFER_ALREADY_EXISTS


def delete_transfer(db: Session, transfer_id: int, user: Optional[User] = None) -> bool:
    """Delete a transfer"""
    # Check if user is admin if authorization is needed
    if user and hasattr(User, 'role') and user.role != 'admin':
        raise TransferException.UNAUTHORIZED
    
    transfer = get_transfer(db, transfer_id)
    
    # Check if transfer is referenced by any itinerary days
    associated_days = db.query(ItineraryDay)\
        .join(ItineraryDay.transfers)\
        .filter(Transfer.id == transfer_id)\
        .first()
        
    if associated_days:
        raise TransferException.TRANSFER_IN_USE
    
    db.delete(transfer)
    db.commit()
    return True