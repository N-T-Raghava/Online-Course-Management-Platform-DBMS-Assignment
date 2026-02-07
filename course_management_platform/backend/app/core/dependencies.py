from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.jwt_handler import decode_access_token
# ------------------------------------------------------------
# Bearer Security Scheme
# ------------------------------------------------------------
security = HTTPBearer()

# ------------------------------------------------------------
# Current User Dependency
# ------------------------------------------------------------

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    token = credentials.credentials

    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    return payload