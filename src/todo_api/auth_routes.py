from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .auth_models import User
from .auth_schemas import UserCreate, UserLogin, UserResponse, Token, TokenData
from .auth_utils import (
    hash_password,
    verify_password,
    create_access_token,
    verify_access_token,
)
from .database import get_db

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


@auth_router.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    exisging_email = db.query(User).filter(User.email == user.email).first()
    if exisging_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    hashed_password = hash_password(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Return the created user without the password
    return new_user


@auth_router.post("/login", response_model=Token)
def login_user(user_data: UserLogin, db: Session = Depends(get_db)):
    # Search the user by username
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Username not found",
        )

    # Verify the password
    if not verify_password(user_data.password, existing_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
        )

    # Create a JWT Token
    access_token = create_access_token({"sub": existing_user.username})

    # Return the access token
    return Token(access_token=access_token, token_type="bearer")
