# backend/app/core/role_guards.py

from fastapi import Depends, HTTPException, status

from app.core.dependencies import get_current_user
from app.core.roles import Role, AdminLevel


# GENERIC ROLE GUARD
def require_role(allowed_roles: list[Role]):

    def role_checker(user=Depends(get_current_user)):

        if user["role"] not in [role.value for role in allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role permissions"
            )

        return user

    return role_checker


# ADMIN LEVEL GUARD
def require_admin_level(required_level: AdminLevel):

    def admin_checker(user=Depends(get_current_user)):

        # Ensure admin role first
        if user["role"] != Role.ADMIN.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Administrator access required"
            )

        # Check level
        if user.get("admin_level") != required_level.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"{required_level.value} admin privileges required"
            )

        return user

    return admin_checker