from fastapi import HTTPException, status


class AccommodationException:
    ACCOMMODATION_NOT_FOUND = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Accommodation not found"
    )
    
    ACCOMMODATION_ALREADY_EXISTS = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Accommodation with this name in this destination already exists"
    )
    
    UNAUTHORIZED = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You are not authorized to perform this action"
    )
    
    ACCOMMODATION_IN_USE = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Accommodation is referenced by one or more itineraries and cannot be deleted"
    )
    
    DESTINATION_NOT_FOUND = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Destination not found"
    )
    
    INVALID_PRICE_CATEGORY = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Price category must be between 1 and 5"
    )
    
    INVALID_STARS = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Stars must be between 0 and 5"
    )