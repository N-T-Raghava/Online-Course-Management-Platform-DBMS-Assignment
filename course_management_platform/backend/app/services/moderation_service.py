# backend/app/services/moderation_service.py

from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import date, datetime

from app.models.enrollment import Enrollment


# ============================================================
# FETCH ENROLLMENT HELPER
# ============================================================

def _get_enrollment(db: Session, student_user_id: int, course_id: int):

    enrollment = db.query(Enrollment).filter(
        Enrollment.student_user_id == student_user_id,
        Enrollment.course_id == course_id
    ).first()

    if not enrollment:
        raise HTTPException(
            status_code=404,
            detail="Enrollment record not found"
        )

    return enrollment


# ============================================================
# DELETE REVIEW + RATING
# ============================================================

def delete_review_service(
    db: Session,
    student_user_id: int,
    course_id: int
):

    enrollment = _get_enrollment(
        db,
        student_user_id,
        course_id
    )

    enrollment.rating = None
    enrollment.review_text = None
    enrollment.rated_at = None

    db.commit()

    return {
        "message": "Review and rating removed successfully"
    }


# ============================================================
# OVERRIDE RATING
# ============================================================

def override_rating_service(
    db: Session,
    student_user_id: int,
    course_id: int,
    new_rating: int
):

    if new_rating < 1 or new_rating > 5:
        raise HTTPException(
            status_code=400,
            detail="Rating must be between 1 and 5"
        )

    enrollment = _get_enrollment(
        db,
        student_user_id,
        course_id
    )

    enrollment.rating = new_rating
    enrollment.rated_at = datetime.utcnow()

    db.commit()

    return {
        "message": "Rating overridden successfully",
        "new_rating": new_rating
    }


# ============================================================
# FORCE COURSE COMPLETION
# ============================================================

def force_completion_service(
    db: Session,
    student_user_id: int,
    course_id: int
):

    enrollment = _get_enrollment(
        db,
        student_user_id,
        course_id
    )

    enrollment.completion_status = "Completed"
    enrollment.completion_date = date.today()

    db.commit()

    return {
        "message": "Course marked as completed"
    }