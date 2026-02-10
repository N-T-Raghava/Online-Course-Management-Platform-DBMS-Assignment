from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.course_schema import (
    UniversityCreate,
    UniversityResponse,
    CourseCreate,
    CourseResponse,
    InstructorCourseCreate,
    InstructorCourseResponse
)
from app.services.course_service import (
    create_university_service,
    get_all_universities_service,
    get_all_categories_service,
    get_courses_by_category_service,
    create_course_service,
    get_all_courses_service,
    get_course_by_id_service,
    get_university_by_course_service,
    create_instructor_course_service,
    get_instructor_pending_courses_service
)

# 🔐 Role Guards
from app.core.role_guards import require_role
from app.core.roles import Role
from app.core.dependencies import get_current_user

# Router Config
router = APIRouter(
    prefix="",
    tags=["Academic - Courses"]
)

# ------------------------------------------------------------
# Create University → Admin Only
# ------------------------------------------------------------
@router.post(
    "/universities",
    response_model=UniversityResponse
)
def create_university(
    payload: UniversityCreate,
    db: Session = Depends(get_db),
    admin = Depends(require_role([Role.ADMIN]))
):
    return create_university_service(db, payload)


# ------------------------------------------------------------
# Get Universities → OPEN
# ------------------------------------------------------------
@router.get(
    "/universities",
    response_model=list[UniversityResponse]
)
def get_universities(
    db: Session = Depends(get_db)
):
    return get_all_universities_service(db)


# ------------------------------------------------------------
# Get Course Categories → OPEN
# ------------------------------------------------------------
@router.get(
    "/categories",
    response_model=list[str]
)
def get_categories(
    db: Session = Depends(get_db)
):
    """Get all distinct course categories"""
    return get_all_categories_service(db)


# ------------------------------------------------------------
# Get Courses by Category → OPEN
# ------------------------------------------------------------
@router.get(
    "/courses/category/{category}",
    response_model=list[CourseResponse]
)
def get_courses_by_category(
    category: str,
    db: Session = Depends(get_db)
):
    """Get all courses for a specific category"""
    return get_courses_by_category_service(db, category)


# ------------------------------------------------------------
# Create Course → Admin Only
# ------------------------------------------------------------
@router.post(
    "/courses",
    response_model=CourseResponse
)
def create_course(
    payload: CourseCreate,
    db: Session = Depends(get_db),
    admin = Depends(require_role([Role.ADMIN]))
):
    return create_course_service(db, payload)


# ------------------------------------------------------------
# Get Courses → OPEN
# ------------------------------------------------------------
@router.get(
    "/courses",
    response_model=list[CourseResponse]
)
def get_courses(
    db: Session = Depends(get_db)
):
    return get_all_courses_service(db)


# ------------------------------------------------------------
# Get Course By ID → OPEN
# ------------------------------------------------------------
@router.get(
    "/courses/{course_id}",
    response_model=CourseResponse
)
def get_course_by_id(
    course_id: int,
    db: Session = Depends(get_db)
):
    return get_course_by_id_service(db, course_id)


@router.get(
    "/courses/{course_id}/university",
    response_model=UniversityResponse
)
def get_university_by_course(
    course_id: int,
    db: Session = Depends(get_db)
):
    return get_university_by_course_service(db, course_id)


# ------------------------------------------------------------
# Create Course → Instructor Only (with Pending approval)
# ------------------------------------------------------------
@router.post(
    "/courses/instructor/create",
    response_model=InstructorCourseResponse
)
def create_instructor_course(
    payload: InstructorCourseCreate,
    db: Session = Depends(get_db),
    instructor = Depends(require_role([Role.INSTRUCTOR])),
    current_user = Depends(get_current_user)
):
    """Create a course as an instructor (automatically set to Pending approval)"""
    return create_instructor_course_service(db, payload, current_user['user_id'])


# ------------------------------------------------------------
# Get Instructor's Pending Courses
# ------------------------------------------------------------
@router.get(
    "/courses/instructor/pending",
    response_model=list[InstructorCourseResponse]
)
def get_instructor_pending(
    db: Session = Depends(get_db),
    instructor = Depends(require_role([Role.INSTRUCTOR])),
    current_user = Depends(get_current_user)
):
    """Get courses pending approval created by current instructor"""
    return get_instructor_pending_courses_service(db, current_user['user_id'])