from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List

# Fix imports to use src prefix
from src.database import get_db
from src.auth import service
from src.auth.models import User
from src.auth.schemas import UserCreate, UserLogin, UserUpdate, UserResponse, Token, UserRole, UserPasswordChange
from src.auth.exceptions import AuthException

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    """Register a new user account"""
    return service.create_user(db, user_data)


@router.post("/login", response_model=Token)
def login(
    user_credentials: UserLogin,
    db: Session = Depends(get_db),
):
    """Login and get access token"""
    user = service.authenticate_user(db, user_credentials.email, user_credentials.password)
    
    access_token_expires = timedelta(minutes=service.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = service.create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(service.get_current_active_user),
):
    """Get current user information"""
    return current_user


@router.put("/me", response_model=UserResponse)
def update_user_info(
    user_update: UserUpdate,
    current_user: User = Depends(service.get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update current user information"""
    # Update user fields if provided
    if user_update.first_name is not None:
        current_user.first_name = user_update.first_name
    
    if user_update.last_name is not None:
        current_user.last_name = user_update.last_name
    
    if user_update.email is not None and user_update.email != current_user.email:
        # Check if email is already in use
        existing_user = service.get_user_by_email(db, user_update.email)
        if existing_user:
            raise AuthException.EMAIL_ALREADY_REGISTERED
        current_user.email = user_update.email
    
    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/change-password")
def change_password(
    password_change: UserPasswordChange,
    current_user: User = Depends(service.get_current_active_user),
    db: Session = Depends(get_db),
):
    """Change user password"""
    # Verify current password
    if not service.verify_password(password_change.current_password, current_user.hashed_password):
        raise AuthException.INVALID_CURRENT_PASSWORD
    
    # Update password
    service.update_password(db, current_user, password_change.new_password)
    return {"message": "Password updated successfully"}


# Admin endpoints
@router.get("/users", response_model=List[UserResponse])
def get_all_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(service.is_admin),
    db: Session = Depends(get_db),
):
    """Get all users (admin only)"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    current_user: User = Depends(service.is_admin),
    db: Session = Depends(get_db),
):
    """Get user by ID (admin only)"""
    user = service.get_user_by_id(db, user_id)
    if not user:
        raise AuthException.USER_NOT_FOUND
    return user


@router.post("/users/create-admin", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_admin_user(
    user_data: UserCreate,
    current_user: User = Depends(service.is_admin),
    db: Session = Depends(get_db),
):
    """Create a new admin user (admin only)"""
    return service.create_user(db, user_data, role=UserRole.ADMIN)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    current_user: User = Depends(service.is_admin),
    db: Session = Depends(get_db),
):
    """Delete a user (admin only)"""
    user = service.get_user_by_id(db, user_id)
    if not user:
        raise AuthException.USER_NOT_FOUND
    
    # Prevent admin from deleting themselves
    if user.id == current_user.id:
        raise AuthException.INSUFFICIENT_PERMISSIONS
    
    db.delete(user)
    db.commit()
    return None