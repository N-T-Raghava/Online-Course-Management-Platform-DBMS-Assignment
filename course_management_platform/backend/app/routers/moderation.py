# backend/app/routers/moderation.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db

# Guards
from app.core.role_guards import require_admin_level
from app.core.roles import AdminLevel

# Services
from app.services.moderation_service import (
    delete_review_service,
    override_rating_service,
    force_completion_service
)

router = APIRouter(
    prefix="/moderation",
    tags=["Administration - Moderation"]
)

# ------------------------------------------------------------
# DELETE REVIEW
# ------------------------------------------------------------
@router.delete("/review/{student_user_id}/{course_id}")
def delete_review(
    student_user_id: int,
    course_id: int,
    db: Session = Depends(get_db),
    admin = Depends(require_admin_level(AdminLevel.SENIOR))
):
    return delete_review_service(
        db,
        student_user_id,
        course_id
    )


# ------------------------------------------------------------
# OVERRIDE RATING
# ------------------------------------------------------------
@router.put("/rating/{student_user_id}/{course_id}/{rating}")
def override_rating(
    student_user_id: int,
    course_id: int,
    rating: int,
    db: Session = Depends(get_db),
    admin = Depends(require_admin_level(AdminLevel.SENIOR))
):
    return override_rating_service(
        db,
        student_user_id,
        course_id,
        rating
    )


# ------------------------------------------------------------
# FORCE COMPLETION
# ------------------------------------------------------------
@router.put("/completion/{student_user_id}/{course_id}")
def force_completion(
    student_user_id: int,
    course_id: int,
    db: Session = Depends(get_db),
    admin = Depends(require_admin_level(AdminLevel.SENIOR))
):
    return force_completion_service(
        db,
        student_user_id,
        course_id
    )