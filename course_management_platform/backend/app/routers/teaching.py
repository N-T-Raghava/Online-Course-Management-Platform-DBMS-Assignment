from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.teaching_schema import TeachingAssign
from app.services.participation_service import (
    assign_instructor_service,
    get_instructor_courses_service
)
from app.repositories.participation_repo import (
    get_instructors_by_course
)

# 🔐 Role Guards
from app.core.role_guards import require_role
from app.core.roles import Role

# Router Config
router = APIRouter(
    prefix="/teaching",
    tags=["Participation - Teaching"]
)

# ------------------------------------------------------------
# Assign Instructor → Junior Admin +
# ------------------------------------------------------------
@router.post("/assign")
def assign_instructor(
    payload: TeachingAssign,
    db: Session = Depends(get_db),
    admin = Depends(require_role([Role.ADMIN]))
):
    return assign_instructor_service(
        db,
        payload.instructor_user_id,
        payload.course_id,
        payload.assigned_date,
        payload.role_in_course
    )


# ------------------------------------------------------------
# Get Instructors By Course → OPEN
# ------------------------------------------------------------
@router.get("/course/{course_id}")
def get_instructors(
    course_id: int,
    db: Session = Depends(get_db)
):
    return get_instructors_by_course(
        db,
        course_id
    )


# ------------------------------------------------------------
# Get Courses By Instructor → OPEN
# ------------------------------------------------------------
@router.get("/instructor/{instructor_user_id}")
def get_instructor_courses(
    instructor_user_id: int,
    db: Session = Depends(get_db)
):
    return get_instructor_courses_service(
        db,
        instructor_user_id
    )
