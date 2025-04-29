from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from auth.models import User
from auth.service import get_current_active_user, is_admin
from activity import service
from activity.schemas import (
    ActivityCreate, 
    ActivityUpdate, 
    ActivityResponse,
    ActivityFilter
)
from models import ActivityCategory

router = APIRouter(
    prefix="/activities",
    tags=["activities"],
)


@router.post("/", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
def create_activity(
    activity_data: ActivityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin),
):
    """
    Create a new activity.
    
    Admin access is required.
    """
    return service.create_activity(db, activity_data, current_user)


@router.get("/", response_model=List[ActivityResponse])
def get_activities(
    skip: int = 0,
    limit: int = 100,
    destination_id: Optional[int] = None,
    category: Optional[ActivityCategory] = None,
    is_must_see: Optional[bool] = None,
    min_duration: Optional[float] = None,
    max_duration: Optional[float] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Get a list of activities with optional filtering.
    
    Supports filtering by:
    - destination_id
    - activity category
    - must-see status
    - duration range
    - search term (searches in name, description, and location)
    """
    filters = None
    if any([destination_id, category, is_must_see is not None, 
           min_duration is not None, max_duration is not None, search]):
        filters = ActivityFilter(
            destination_id=destination_id,
            category=category,
            is_must_see=is_must_see,
            min_duration=min_duration,
            max_duration=max_duration,
            search=search
        )
    
    return service.get_activities(db, skip, limit, filters)


@router.get("/{activity_id}", response_model=ActivityResponse)
def get_activity(
    activity_id: int,
    db: Session = Depends(get_db),
):
    """
    Get detailed information about a specific activity by ID.
    """
    return service.get_activity(db, activity_id)


@router.put("/{activity_id}", response_model=ActivityResponse)
def update_activity(
    activity_id: int,
    activity_data: ActivityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin),
):
    """
    Update an existing activity.
    
    Admin access is required.
    """
    return service.update_activity(db, activity_id, activity_data, current_user)


@router.patch("/{activity_id}", response_model=ActivityResponse)
def partial_update_activity(
    activity_id: int,
    activity_data: ActivityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin),
):
    """
    Partially update an existing activity.
    
    This is an alias for the PUT endpoint for clients that prefer PATCH semantics.
    Admin access is required.
    """
    return service.update_activity(db, activity_id, activity_data, current_user)


@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin),
):
    """
    Delete an activity.
    
    This operation cannot be performed if the activity is referenced by any itineraries.
    Admin access is required.
    """
    service.delete_activity(db, activity_id, current_user)
    return None