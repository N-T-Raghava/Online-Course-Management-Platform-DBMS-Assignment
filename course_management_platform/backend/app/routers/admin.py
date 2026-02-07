from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db

# Guards
from app.core.role_guards import require_admin_level
from app.core.roles import AdminLevel

# Services
from app.services.admin_service import (
    delete_user_service,
    remove_instructor_service
)

router = APIRouter(
    prefix="/admin",
    tags=["Administration"]
)

# ------------------------------------------------------------
# DELETE USER → Senior Admin Only
# ------------------------------------------------------------
@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin = Depends(require_admin_level(AdminLevel.SENIOR))
):
    return delete_user_service(db, user_id)


# ------------------------------------------------------------
# REMOVE INSTRUCTOR FROM COURSE → Senior Only
# ------------------------------------------------------------
@router.delete("/teaching/{course_id}/{instructor_user_id}")
def remove_instructor(
    course_id: int,
    instructor_user_id: int,
    db: Session = Depends(get_db),
    admin = Depends(require_admin_level(AdminLevel.SENIOR))
):
    return remove_instructor_service(
        db,
        course_id,
        instructor_user_id
    )