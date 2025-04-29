from fastapi import HTTPException, status

class ItineraryException:
    ITINERARY_NOT_FOUND = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Itinerary not found"
    )
    
    UNAUTHORIZED = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You are not authorized to perform this action"
    )
    
    INVALID_DAY_NUMBER = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid day number for this itinerary"
    )
    
    DESTINATION_NOT_FOUND = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Destination not found"
    )
    
    ACCOMMODATION_NOT_FOUND = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Accommodation not found"
    )
    
    ACTIVITY_NOT_FOUND = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Activity not found"
    )
    
    TRANSFER_NOT_FOUND = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Transfer not found"
    )
    
    DAYS_MISMATCH = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Number of days does not match the duration nights"
    )
    
    DAY_ALREADY_EXISTS = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Day already exists for this itinerary"
    )
