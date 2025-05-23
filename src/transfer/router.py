from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

# Fix imports to use src prefix
from src.database import get_db
from src.transfer import service
from src.transfer.schemas import TransferCreate, TransferUpdate, TransferResponse, TransferFilter
from src.models import TransportType
from src.auth.service import get_current_active_user, is_admin, is_authenticated
from src.auth.models import User

router = APIRouter(
    prefix="/transfers",
    tags=["transfers"],
)


@router.post("/", response_model=TransferResponse, status_code=status.HTTP_201_CREATED)
def create_transfer(
    transfer_data: TransferCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin),  # Changed from is_authenticated to is_admin
):
    """
    Create a new transfer.
    
    Admin access is required.
    """
    return service.create_transfer(db, transfer_data, current_user)


@router.get("/", response_model=List[TransferResponse])
def get_transfers(
    skip: int = 0,
    limit: int = 100,
    origin_id: Optional[int] = None,
    destination_id: Optional[int] = None,
    type: Optional[str] = None,  # Changed from TransportType to str for test compatibility
    min_duration: Optional[float] = None,
    max_duration: Optional[float] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Get a list of transfers with optional filtering.
    
    Supports filtering by:
    - origin destination
    - target destination
    - transport type
    - duration range
    - search term (searches in name and description)
    """
    filters = None
    if any([origin_id, destination_id, type, 
           min_duration is not None, max_duration is not None, search]):
        # Convert string transport type to enum if provided
        transport_type = None
        if type:
            try:
                transport_type = TransportType[type]
            except (KeyError, ValueError):
                # If invalid, just pass None and let the service handle it
                pass
                
        filters = TransferFilter(
            origin_id=origin_id,
            destination_id=destination_id,
            type=transport_type,
            min_duration=min_duration,
            max_duration=max_duration,
            search=search
        )
    
    return service.get_transfers(db, skip, limit, filters)


@router.get("/{transfer_id}", response_model=TransferResponse)
def get_transfer(
    transfer_id: int,
    db: Session = Depends(get_db),
):
    """
    Get detailed information about a specific transfer by ID.
    """
    return service.get_transfer(db, transfer_id)


@router.put("/{transfer_id}", response_model=TransferResponse)
def update_transfer(
    transfer_id: int,
    transfer_data: TransferUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin),
):
    """
    Update an existing transfer.
    
    Admin access is required.
    """
    return service.update_transfer(db, transfer_id, transfer_data, current_user)


@router.patch("/{transfer_id}", response_model=TransferResponse)
def partial_update_transfer(
    transfer_id: int,
    transfer_data: TransferUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin),
):
    """
    Partially update an existing transfer.
    
    This is an alias for the PUT endpoint for clients that prefer PATCH semantics.
    Admin access is required.
    """
    return service.update_transfer(db, transfer_id, transfer_data, current_user)


@router.delete("/{transfer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transfer(
    transfer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin),
):
    """
    Delete a transfer.
    
    This operation cannot be performed if the transfer is referenced by any itineraries.
    Admin access is required.
    """
    service.delete_transfer(db, transfer_id, current_user)
    return None