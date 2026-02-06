from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.teaching_schema import TeachingAssign
from app.services.participation_service import (
    assign_instructor_service
)
from app.repositories.participation_repo import (
    get_instructors_by_course
)

# Router Config

router = APIRouter(
    prefix="/teaching",
    tags=["Participation - Teaching"]
)

# Assign Instructor

@router.post("/assign")
def assign_instructor(
    payload: TeachingAssign,
    db: Session = Depends(get_db)
):
    return assign_instructor_service(
        db,
        payload.instructor_user_id,
        payload.course_id,
        payload.assigned_date,
        payload.role_in_course
    )


# Get Instructors By Course
@router.get("/course/{course_id}")
def get_instructors(
    course_id: int,
    db: Session = Depends(get_db)
):
    return get_instructors_by_course(
        db,
        course_id
    )