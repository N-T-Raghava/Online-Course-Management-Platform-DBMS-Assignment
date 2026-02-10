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
from app.services.statistics_service import (
    recompute_all_students_service,
    recompute_all_instructors_service,
    recompute_all_courses_service,
    recompute_platform_service
)
from app.core.dependencies import get_current_user
from app.core.role_guards import require_role
from app.core.roles import Role
from app.services.admin_service import get_course_students_service
from app.services.admin_service import get_student_profile_service
from app.models.teaching import Teaching
from app.models.enrollment import Enrollment
from app.models.user import User

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


@router.get('/courses/{course_id}/students')
def get_course_students_for_instructor(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Return students enrolled in a course for the instructor assigned to it."""
    # Ensure requester is the instructor for this course
    user_role = current_user.get('role', '').lower()
    if user_role != Role.INSTRUCTOR.value.lower():
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail='Only instructors can access this endpoint')

    # Verify teaching assignment
    teaching = db.query(Teaching).filter(
        Teaching.course_id == course_id,
        Teaching.instructor_user_id == current_user.get('user_id')
    ).first()

    if not teaching:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail='You are not assigned to this course')

    # Reuse admin service implementation to fetch students (service is not tied to admin guard)
    return get_course_students_service(db, course_id)


# Instructor: view a specific student profile if the instructor teaches one of the student's courses
@router.get('/instructor/students/{student_user_id}')
def get_student_profile_for_instructor(
    student_user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_role = (current_user.get('role') or '').lower()
    if user_role != Role.INSTRUCTOR.value.lower():
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail='Only instructors can access this endpoint')

    # Get list of course_ids the instructor teaches
    teaching_courses = db.query(Teaching.course_id).filter(
        Teaching.instructor_user_id == current_user.get('user_id')
    ).all()

    teaching_course_ids = {t[0] for t in teaching_courses}

    # Check if student is enrolled in any of these courses
    enrollment_exists = db.query(Enrollment).filter(
        Enrollment.student_user_id == student_user_id,
        Enrollment.course_id.in_(list(teaching_course_ids))
    ).first() if teaching_course_ids else None

    if not enrollment_exists:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail='You are not assigned to any course this student is enrolled in')

    return get_student_profile_service(db, student_user_id)


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


# ---------------- Batch Recompute Endpoints ----------------
@router.post('/recompute/students')
def recompute_all_students(db: Session = Depends(get_db)):
    """Recompute stats for all students (only where Student record exists)."""
    return recompute_all_students_service(db)


@router.post('/recompute/instructors')
def recompute_all_instructors(db: Session = Depends(get_db)):
    """Recompute stats for all instructors (only where Instructor record exists)."""
    return recompute_all_instructors_service(db)


@router.post('/recompute/courses')
def recompute_all_courses(db: Session = Depends(get_db)):
    """Recompute stats for all courses."""
    return recompute_all_courses_service(db)


@router.post('/recompute/platform')
def recompute_platform(db: Session = Depends(get_db)):
    """Recompute statistics for the entire platform (students, instructors, courses)."""
    return recompute_platform_service(db)