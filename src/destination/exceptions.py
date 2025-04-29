from fastapi import HTTPException, status


class DestinationException:
    DESTINATION_NOT_FOUND = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Destination not found"
    )
    
    DESTINATION_ALREADY_EXISTS = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Destination with this name and region already exists"
    )
    
    UNAUTHORIZED = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You are not authorized to perform this action"
    )
    
    DESTINATION_IN_USE = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Destination is referenced by one or more itineraries and cannot be deleted"
    )
