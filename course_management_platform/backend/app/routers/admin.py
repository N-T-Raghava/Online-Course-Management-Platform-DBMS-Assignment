from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db

# Guards
from app.core.role_guards import require_admin_level, require_role
from app.core.roles import AdminLevel, Role
from app.core.dependencies import get_current_user

# Services
from app.services.admin_service import (
    # Junior Admin services
    get_all_courses_admin_service,
    get_pending_courses_service,
    get_course_details_admin_service,
    get_course_statistics_admin_service,
    get_course_ratings_admin_service,
    approve_course_service,
    reject_course_service,
    get_course_students_service,
    get_student_profile_service,
    # Senior Admin services
    delete_user_service,
    remove_instructor_service,
    delete_course_request_service,
    delete_public_rating_service
)

router = APIRouter(
    prefix="/admin",
    tags=["Administration"]
)


# ============================================================
# SCHEMAS FOR REQUEST BODIES
# ============================================================

class RejectCourseRequest(BaseModel):
    reason: str = None


# ============================================================
# JUNIOR ADMIN: GET ALL COURSES
# ============================================================
@router.get("/courses")
def get_all_courses(
    db: Session = Depends(get_db),
    admin = Depends(require_admin_level(AdminLevel.JUNIOR))
):
    return get_all_courses_admin_service(db)


# ============================================================
# JUNIOR ADMIN: GET PENDING COURSES ONLY
# ============================================================
@router.get("/courses/pending/list")
def get_pending_courses(
    db: Session = Depends(get_db),
    admin = Depends(require_admin_level(AdminLevel.JUNIOR))
):
    return get_pending_courses_service(db)


# ============================================================
# JUNIOR ADMIN: GET COURSE DETAILS
# ============================================================
@router.get("/courses/{course_id}")
def get_course_details(
    course_id: int,
    db: Session = Depends(get_db),
    admin = Depends(require_admin_level(AdminLevel.JUNIOR))
):
    return get_course_details_admin_service(db, course_id)


# ============================================================
# JUNIOR ADMIN: GET COURSE STATISTICS
# ============================================================
@router.get("/courses/{course_id}/statistics")
def get_course_statistics(
    course_id: int,
    db: Session = Depends(get_db),
    admin = Depends(require_admin_level(AdminLevel.JUNIOR))
):
    return get_course_statistics_admin_service(db, course_id)


# ============================================================
# JUNIOR ADMIN: GET COURSE RATINGS AND REVIEWS
# ============================================================
@router.get("/courses/{course_id}/ratings")
def get_course_ratings(
    course_id: int,
    db: Session = Depends(get_db),
    admin = Depends(require_admin_level(AdminLevel.JUNIOR))
):
    return get_course_ratings_admin_service(db, course_id)


# ============================================================
# JUNIOR ADMIN: APPROVE COURSE
# ============================================================
@router.put("/courses/{course_id}/approve")
def approve_course(
    course_id: int,
    db: Session = Depends(get_db),
    admin = Depends(require_admin_level(AdminLevel.JUNIOR))
):
    return approve_course_service(db, course_id, admin["user_id"])


# ============================================================
# JUNIOR ADMIN: REJECT COURSE
# ============================================================
@router.put("/courses/{course_id}/reject")
def reject_course(
    course_id: int,
    payload: RejectCourseRequest,
    db: Session = Depends(get_db),
    admin = Depends(require_admin_level(AdminLevel.JUNIOR))
):
    return reject_course_service(db, course_id, payload.reason)


# ============================================================
# SENIOR ADMIN: DELETE COURSE REQUEST
# ============================================================
@router.delete("/courses/{course_id}")
def delete_course_request(
    course_id: int,
    db: Session = Depends(get_db),
    admin = Depends(require_admin_level(AdminLevel.SENIOR))
):
    return delete_course_request_service(db, course_id)


# ============================================================
# SENIOR ADMIN: DELETE PUBLIC RATING
# ============================================================
@router.delete("/ratings/{student_user_id}/{course_id}")
def delete_public_rating(
    student_user_id: int,
    course_id: int,
    db: Session = Depends(get_db),
    admin = Depends(require_admin_level(AdminLevel.SENIOR))
):
    return delete_public_rating_service(db, student_user_id, course_id)


# ============================================================
# DELETE USER → Senior Admin Only
# ============================================================
@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin = Depends(require_admin_level(AdminLevel.SENIOR))
):
    return delete_user_service(db, user_id)


# ============================================================
# REMOVE INSTRUCTOR FROM COURSE → Senior Only
# ============================================================
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


# ============================================================
# GET STUDENTS ENROLLED IN COURSE → Junior Admin
# ============================================================
@router.get("/courses/{course_id}/students")
def get_course_students(
    course_id: int,
    db: Session = Depends(get_db),
    admin = Depends(require_admin_level(AdminLevel.JUNIOR))
):
    return get_course_students_service(db, course_id)


# ============================================================
# GET STUDENT PROFILE → Admin or Instructor
# ============================================================
@router.get("/students/{student_user_id}")
def get_student_profile(
    student_user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get student profile (accessible by admins and instructors)"""
    user_role = current_user.get('role', '').lower()
    # Allow admin or instructor role
    if user_role not in [Role.ADMIN.value.lower(), Role.INSTRUCTOR.value.lower()]:
        raise HTTPException(status_code=403, detail='Permission denied')
    
    return get_student_profile_service(db, student_user_id)
