from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.security import hash_password, verify_password
from app.core.jwt_handler import create_access_token

from app.repositories import user_repo
from app.schemas.auth_schema import RegisterRequest

# Register User
def register_user(db: Session, payload: RegisterRequest):

    # Check duplicate email
    existing_user = user_repo.get_user_by_email(db, payload.email)

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash password
    hashed_pw = hash_password(payload.password)

    # Create base user
    user_data = {
        "name": payload.name,
        "email": payload.email,
        "password": hashed_pw,
        "phone_number": payload.phone_number,
        "role": payload.role
    }

    user = user_repo.create_user(db, user_data)

    # Insert subclass
    role = payload.role.lower()

    if role == "student":
        user_repo.create_student(db, user.user_id, {
            "date_of_birth": payload.date_of_birth,
            "country": payload.country,
            "gender": payload.gender,
            "education_level": payload.education_level
        })

    elif role == "instructor":
        user_repo.create_instructor(db, user.user_id, {
            "qualification": payload.qualification,
            "experience": payload.experience,
            "expertise_area": payload.expertise_area,
            "bio": payload.bio
        })

    elif role == "administrator":
        user_repo.create_administrator(db, user.user_id, {
            "admin_level": payload.admin_level,
            "assigned_since": payload.assigned_since
        })

    elif role == "dataanalyst":
        user_repo.create_data_analyst(db, user.user_id, {
            "qualification": payload.analyst_qualification
        })

    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid role"
        )

    return user

# Login User
def login_user(db: Session, email: str, password: str):

    # Fetch user
    user = user_repo.get_user_by_email(db, email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Verify password
    if not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Generate token
    token_data = {
        "user_id": user.user_id,
        "role": user.role
    }

    access_token = create_access_token(token_data)

    return {
        "access_token": access_token,
        "token_type": "Bearer",
        "user_id": user.user_id,
        "role": user.role
    }