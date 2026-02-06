from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date

# Register Schema
class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)
    phone_number: Optional[str]

    role: str = Field(
        ...,
        description="Student / Instructor / Administrator / DataAnalyst"
    )

    # --- Student Fields ---
    date_of_birth: Optional[date]
    country: Optional[str]
    gender: Optional[str]
    education_level: Optional[str]

    # --- Instructor Fields ---
    qualification: Optional[str]
    experience: Optional[int]
    expertise_area: Optional[str]
    bio: Optional[str]

    # --- Admin Fields ---
    admin_level: Optional[str]
    assigned_since: Optional[date]

    # --- Analyst Fields ---
    analyst_qualification: Optional[str]


# Login Schema
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# Token Response Schema
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    user_id: int
    role: str

# User Response Schema
class UserResponse(BaseModel):
    user_id: int
    name: str
    email: str
    role: str

    class Config:
        orm_mode = True