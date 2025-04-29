from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import Depends, Header
import os
from dotenv import load_dotenv

from database import get_db
from auth.models import User, UserRole
from auth.schemas import UserCreate, TokenData
from auth.exceptions import AuthException

load_dotenv()

# Security configurations
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-placeholder")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify if the provided password matches the hashed password"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password for storing"""
    return pwd_context.hash(password)


def create_user(db: Session, user_data: UserCreate, role: UserRole = UserRole.USER) -> User:
    """Create a new user with the given role (default: regular user)"""
    # Check if user already exists
    db_user = db.query(User).filter(User.email == user_data.email).first()
    if db_user:
        raise AuthException.EMAIL_ALREADY_REGISTERED
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        hashed_password=hashed_password,
        role=role
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, email: str, password: str) -> User:
    """Verify user credentials and return user if valid"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise AuthException.INCORRECT_EMAIL_OR_PASSWORD
    
    if not verify_password(password, user.hashed_password):
        raise AuthException.INCORRECT_EMAIL_OR_PASSWORD
    
    if not user.is_active:
        raise AuthException.INACTIVE_USER
    
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token with optional expiration time"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(db: Session = Depends(get_db), authorization: str = Header(None)) -> User:
    """Decode JWT token and return current user"""
    if authorization is None:
        raise AuthException.CREDENTIALS_EXCEPTION
        
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise AuthException.CREDENTIALS_EXCEPTION
            
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise AuthException.CREDENTIALS_EXCEPTION
            
        token_data = TokenData(user_id=int(user_id))
    except (JWTError, ValueError):
        raise AuthException.CREDENTIALS_EXCEPTION
        
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if user is None:
        raise AuthException.CREDENTIALS_EXCEPTION
        
    if not user.is_active:
        raise AuthException.INACTIVE_USER
        
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Check if current user is active"""
    if not current_user.is_active:
        raise AuthException.INACTIVE_USER
    return current_user


def is_admin(current_user: User = Depends(get_current_user)) -> User:
    """Check if user has admin role"""
    if current_user.role != UserRole.ADMIN:
        raise AuthException.INSUFFICIENT_PERMISSIONS
    return current_user


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()


def update_password(db: Session, user: User, new_password: str) -> User:
    """Update user password"""
    user.hashed_password = get_password_hash(new_password)
    db.commit()
    db.refresh(user)
    return user