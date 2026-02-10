from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.analyst_service import (
    get_platform_overview_service,
    get_all_courses_analytics_service,
    get_all_students_analytics_service,
    get_all_instructors_analytics_service,
    get_course_detailed_analytics_service
)
from app.core.role_guards import require_role
from app.core.roles import Role
from app.services.admin_service import get_student_profile_service
from sqlalchemy.orm import Session
from app.database import get_db
from fastapi import Depends
import re

# Router Config
router = APIRouter(
    prefix="/analyst",
    tags=["Data Analyst Dashboard"]
)

# PLATFORM OVERVIEW
@router.get("/overview")
def get_platform_overview(db: Session = Depends(get_db)):
    """Get platform-wide overview statistics"""
    return get_platform_overview_service(db)


# COURSES ANALYTICS
@router.get("/courses/analytics")
def get_courses_analytics(db: Session = Depends(get_db)):
    """Get analytics for all courses"""
    return get_all_courses_analytics_service(db)


@router.get("/courses/{course_id}/detailed")
def get_course_detailed_analytics(course_id: int, db: Session = Depends(get_db)):
    """Get detailed analytics for a specific course including enrolled students"""
    return get_course_detailed_analytics_service(db, course_id)


# STUDENTS ANALYTICS
@router.get("/students/analytics")
def get_students_analytics(db: Session = Depends(get_db)):
    """Get analytics for all students on the platform"""
    return get_all_students_analytics_service(db)


# Analyst: Get individual student profile
@router.get("/students/{student_user_id}")
def get_student_profile_for_analyst(
    student_user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(__import__('app.core.dependencies', fromlist=['get_current_user']).get_current_user)
):
    """Return student profile for analysts (role-guarded). This endpoint normalizes role strings to
    accept variations like 'DataAnalyst', 'dataanalyst', or 'Data Analyst'."""
    # Debug print of current user payload
    print(f"[DEBUG][analyst.student_profile] current_user payload: {current_user}")

    raw_role = current_user.get('role') or ''
    # normalize by removing non-alphanumeric characters and lowercasing
    normalized = re.sub(r"[^a-z0-9]", "", raw_role.lower())
    allowed = [re.sub(r"[^a-z0-9]", "", Role.ANALYST.value.lower())]
    print(f"[DEBUG][analyst.student_profile] raw_role='{raw_role}', normalized='{normalized}', allowed={allowed}")

    if normalized not in allowed:
        from fastapi import HTTPException
        print(f"[DEBUG][analyst.student_profile] access denied for role '{raw_role}' (normalized '{normalized}')")
        raise HTTPException(status_code=403, detail='Insufficient role permissions')

    return get_student_profile_service(db, student_user_id)


# INSTRUCTORS ANALYTICS
@router.get("/instructors/analytics")
def get_instructors_analytics(db: Session = Depends(get_db)):
    """Get analytics for all instructors on the platform"""
    return get_all_instructors_analytics_service(db)
