from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date


# ============================================================
# REGISTER REQUEST — ROLE DYNAMIC
# ============================================================

class RegisterRequest(BaseModel):

    # --------------------------------------------------------
    # BASE USER FIELDS (REQUIRED)
    # --------------------------------------------------------

    name: str = Field(..., min_length=2, max_length=100)

    email: EmailStr

    password: str = Field(..., min_length=6)

    phone_number: Optional[str] = None

    role: str = Field(
        ...,
        description="Student / Instructor / Administrator / DataAnalyst"
    )

    # --------------------------------------------------------
    # STUDENT FIELDS (OPTIONAL)
    # --------------------------------------------------------

    date_of_birth: Optional[date] = None

    country: Optional[str] = None

    gender: Optional[str] = None

    education_level: Optional[str] = None

    # --------------------------------------------------------
    # INSTRUCTOR FIELDS (OPTIONAL)
    # --------------------------------------------------------

    qualification: Optional[str] = None

    experience: Optional[int] = None

    expertise_area: Optional[str] = None

    bio: Optional[str] = None

    # --------------------------------------------------------
    # ADMINISTRATOR FIELDS (OPTIONAL)
    # --------------------------------------------------------

    admin_level: Optional[str] = None

    assigned_since: Optional[date] = None

    # --------------------------------------------------------
    # ANALYST FIELDS (OPTIONAL)
    # --------------------------------------------------------

    analyst_qualification: Optional[str] = None


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