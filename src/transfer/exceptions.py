from fastapi import HTTPException, status


class TransferException:
    TRANSFER_NOT_FOUND = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Transfer not found"
    )
    
    TRANSFER_ALREADY_EXISTS = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Transfer with this name between these destinations already exists"
    )
    
    UNAUTHORIZED = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You are not authorized to perform this action"
    )
    
    TRANSFER_IN_USE = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Transfer is referenced by one or more itineraries and cannot be deleted"
    )
    
    DESTINATION_NOT_FOUND = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Destination not found"
    )
    
    SAME_DESTINATIONS = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Origin and destination must be different"
    )
    
    INVALID_DURATION = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Duration hours must be positive"
    )