from fastapi import HTTPException, status


class ActivityException:
    ACTIVITY_NOT_FOUND = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Activity not found"
    )
    
    ACTIVITY_ALREADY_EXISTS = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Activity with this name in this destination already exists"
    )
    
    UNAUTHORIZED = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You are not authorized to perform this action"
    )
    
    ACTIVITY_IN_USE = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Activity is referenced by one or more itineraries and cannot be deleted"
    )
    
    DESTINATION_NOT_FOUND = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Destination not found"
    )
    
    INVALID_DURATION = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Duration hours must be positive"
    )