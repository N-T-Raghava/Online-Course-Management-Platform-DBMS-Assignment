from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db

from app.services.statistics_service import (
    get_course_statistics_service,
    get_student_statistics_service,
    get_instructor_statistics_service,
    update_course_statistics_service,
    update_student_statistics_service,
    update_instructor_statistics_service
)

# Router Config

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics & Statistics"]
)

# FETCH ANALYTICS

# ---------------- Course Stats --------------------

@router.get("/courses/{course_id}")
def get_course_analytics(
    course_id: int,
    db: Session = Depends(get_db)
):
    return get_course_statistics_service(
        db,
        course_id
    )


# ---------------- Student Stats -------------------

@router.get("/students/{student_user_id}")
def get_student_analytics(
    student_user_id: int,
    db: Session = Depends(get_db)
):
    return get_student_statistics_service(
        db,
        student_user_id
    )


# ---------------- Instructor Stats ----------------

@router.get("/instructors/{instructor_user_id}")
def get_instructor_analytics(
    instructor_user_id: int,
    db: Session = Depends(get_db)
):
    return get_instructor_statistics_service(
        db,
        instructor_user_id
    )


# RECOMPUTE ANALYTICS

# ---------------- Course Recompute ----------------

@router.post("/recompute/course/{course_id}")
def recompute_course_stats(
    course_id: int,
    db: Session = Depends(get_db)
):
    return update_course_statistics_service(
        db,
        course_id
    )


# ---------------- Student Recompute ---------------

@router.post("/recompute/student/{student_user_id}")
def recompute_student_stats(
    student_user_id: int,
    db: Session = Depends(get_db)
):
    return update_student_statistics_service(
        db,
        student_user_id
    )


# ---------------- Instructor Recompute ------------

@router.post("/recompute/instructor/{instructor_user_id}")
def recompute_instructor_stats(
    instructor_user_id: int,
    db: Session = Depends(get_db)
):
    return update_instructor_statistics_service(
        db,
        instructor_user_id
    )