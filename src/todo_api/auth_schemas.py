from pydantic import BaseModel, EmailStr, ConfigDict


# User registration schema
class UserCreate(BaseModel):
    username: str
    email: EmailStr  # Using EmailStr for email validation
    password: str


# User connection schema
class UserLogin(BaseModel):
    username: str
    password: str


# User response schema
class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


# JWT token schema
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
