from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from datetime import timedelta
from typing import Optional
import bcrypt
import uuid

from models.user import UserInDB, User
from core.database import get_collection
from core.config import settings
from utils.jwt import create_jwt_token
from utils.helper import generate_response, generate_id
from utils.logger import setup_logger

router = APIRouter()
logger = setup_logger("auth")

# Perbaikan: Ubah SignupRequest menjadi model Pydantic
class SignupRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    wallet_address: Optional[str] = None

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: User

@router.post("/signup", response_model=dict)
async def signup(data: SignupRequest):
    """Register a new user"""
    users_collection = get_collection("users")
    
    # Check if username or email already exists
    if await users_collection.find_one({"username": data.username}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    if await users_collection.find_one({"email": data.email}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    password_hash = bcrypt.hashpw(data.password.encode(), bcrypt.gensalt()).decode()
    
    # Create user
    user_id = generate_id("usr_")
    user = UserInDB(
        id=user_id,
        username=data.username,
        email=data.email,
        password_hash=password_hash,
        wallet_address=data.wallet_address
    )
    
    # Save to database
    await users_collection.insert_one(user.dict())
    
    # Create access token
    access_token = create_jwt_token(
        data={"sub": user_id}
    )
    
    # Create user model (without password)
    user_response = User(
        id=user.id,
        username=user.username,
        email=user.email,
        wallet_address=user.wallet_address,
        created_at=user.created_at,
        credits=user.credits,
        role=user.role
    )
    
    return generate_response(
        data={"access_token": access_token, "token_type": "bearer", "user": user_response.dict()},
        message="User registered successfully"
    )

@router.post("/login", response_model=dict)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Authenticate user and return JWT token"""
    users_collection = get_collection("users")
    
    # Find user by username
    user_data = await users_collection.find_one({"username": form_data.username})
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    is_password_valid = bcrypt.checkpw(
        form_data.password.encode(), 
        user_data["password_hash"].encode()
    )
    
    if not is_password_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_jwt_token(
        data={"sub": user_data["id"]},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    # Create user model (without password)
    user = User(
        id=user_data["id"],
        username=user_data["username"],
        email=user_data["email"],
        wallet_address=user_data.get("wallet_address"),
        created_at=user_data["created_at"],
        credits=user_data["credits"],
        role=user_data["role"]
    )
    
    return generate_response(
        data={"access_token": access_token, "token_type": "bearer", "user": user.dict()},
        message="Login successful"
    )
