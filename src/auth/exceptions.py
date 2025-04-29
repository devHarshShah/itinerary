from fastapi import HTTPException, status


class AuthException:
    CREDENTIALS_EXCEPTION = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    INCORRECT_EMAIL_OR_PASSWORD = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    INACTIVE_USER = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Inactive user",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    EMAIL_ALREADY_REGISTERED = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Email already registered",
    )
    
    USER_NOT_FOUND = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found",
    )
    
    INSUFFICIENT_PERMISSIONS = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Insufficient permissions",
    )
    
    INVALID_CURRENT_PASSWORD = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Current password is invalid",
    )