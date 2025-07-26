from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
import secrets


# Configuration for password hashing
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

SECRET_KEY = secrets.token_urlsafe(32)  # Generate a secure random secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Token expiration time in minutes


def hash_password(password: str) -> str:
    """Hash a password using Argon2."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str) -> str | None:
    """Verify a JWT access token and return the username."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        return username
    except JWTError:
        return None
