from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.enrollment_schema import (
    EnrollmentCreate,
    CompletionUpdate,
    RatingUpdate
)
from app.services.participation_service import (
    enroll_student_service,
    update_completion_service,
    rate_course_service
)

# 🔐 Auth Dependency (JWT Payload)
from app.core.dependencies import get_current_user

# Router Config
router = APIRouter(
    prefix="/enrollments",
    tags=["Participation - Enrollment"]
)

# ------------------------------------------------------------
# ENROLL STUDENT
# • Student → Self only
# • Admin → Override allowed
# ------------------------------------------------------------
@router.post("/")
def enroll_student(
    payload: EnrollmentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return enroll_student_service(
        db,
        payload.student_user_id,
        payload.course_id,
        current_user
    )


# ------------------------------------------------------------
# UPDATE COMPLETION
# • Student → Self only
# • Admin → Override allowed
# ------------------------------------------------------------
@router.put("/complete/{student_user_id}/{course_id}")
def update_completion(
    student_user_id: int,
    course_id: int,
    payload: CompletionUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return update_completion_service(
        db,
        student_user_id,
        course_id,
        payload.completion_status,
        payload.completion_date,
        current_user
    )


# ------------------------------------------------------------
# RATE COURSE
# • Student → Self only
# • Admin → Override allowed
# ------------------------------------------------------------
@router.post("/rate/{student_user_id}/{course_id}")
def rate_course(
    student_user_id: int,
    course_id: int,
    payload: RatingUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return rate_course_service(
        db,
        student_user_id,
        course_id,
        payload.rating,
        payload.review_text,
        current_user
    )