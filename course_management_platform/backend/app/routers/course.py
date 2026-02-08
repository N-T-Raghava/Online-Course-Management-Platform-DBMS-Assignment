from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.course_schema import (
    UniversityCreate,
    UniversityResponse,
    CourseCreate,
    CourseResponse
)
from app.services.course_service import (
    create_university_service,
    get_all_universities_service,
    create_course_service,
    get_all_courses_service,
    get_course_by_id_service
    , get_university_by_course_service
)

# 🔐 Role Guards
from app.core.role_guards import require_role
from app.core.roles import Role

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