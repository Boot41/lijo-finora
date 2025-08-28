"""Authentication API routes."""

import logging
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPAuthorizationCredentials

from schemas.auth import UserCreate, UserLogin, UserResponse, Token
from middleware.auth import (
    verify_password, 
    get_password_hash, 
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])

# Mock user database (replace with real database in production)
fake_users_db = {}


@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate):
    """Register a new user."""
    try:
        # Check if user already exists
        if user_data.email in fake_users_db:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password and create user
        hashed_password = get_password_hash(user_data.password)
        user_id = f"user_{len(fake_users_db) + 1}"
        
        fake_users_db[user_data.email] = {
            "id": user_id,
            "email": user_data.email,
            "username": user_data.username,
            "hashed_password": hashed_password,
            "is_active": True
        }
        
        logger.info(f"User registered successfully: {user_data.email}")
        
        return UserResponse(
            id=user_id,
            email=user_data.email,
            username=user_data.username,
            is_active=True,
            created_at=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user"
        )


@router.post("/login", response_model=Token)
async def login_user(user_credentials: UserLogin):
    """Authenticate user and return access token."""
    try:
        # Check if user exists
        user = fake_users_db.get(user_credentials.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify password
        if not verify_password(user_credentials.password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["id"], "email": user["email"]},
            expires_delta=access_token_expires
        )
        
        logger.info(f"User logged in successfully: {user_credentials.email}")
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error logging in user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to authenticate user"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information."""
    try:
        # Find user in database
        user = None
        for email, user_data in fake_users_db.items():
            if user_data["id"] == current_user["user_id"]:
                user = user_data
                break
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse(
            id=user["id"],
            email=user["email"],
            username=user["username"],
            is_active=user["is_active"],
            created_at=datetime.utcnow()  # Mock created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user information"
        )
