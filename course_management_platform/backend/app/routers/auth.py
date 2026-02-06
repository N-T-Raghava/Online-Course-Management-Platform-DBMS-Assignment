from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.database import get_db
from app.schemas.auth_schema import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    UserResponse
)
from app.services.auth_service import (
    register_user,
    login_user
)
from app.core.jwt_handler import decode_access_token
from app.repositories.user_repo import get_user_by_id

# Router Config
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

security = HTTPBearer()

# Register Endpoint
@router.post("/register", response_model=UserResponse)
def register(
    payload: RegisterRequest,
    db: Session = Depends(get_db)
):
    user = register_user(db, payload)

    return {
        "user_id": user.user_id,
        "name": user.name,
        "email": user.email,
        "role": user.role
    }

# Login Endpoint
@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db)
):
    return login_user(
        db,
        payload.email,
        payload.password
    )

# Get Current User
@router.get("/me", response_model=UserResponse)
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    user = get_user_by_id(db, payload["user_id"])

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return {
        "user_id": user.user_id,
        "name": user.name,
        "email": user.email,
        "role": user.role
    }