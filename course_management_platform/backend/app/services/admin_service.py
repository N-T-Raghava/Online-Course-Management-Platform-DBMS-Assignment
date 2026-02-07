# backend/app/services/admin_service.py

from fastapi import HTTPException
from sqlalchemy.orm import Session

# Models
from app.models.user import User
from app.models.teaching import Teaching

# ISA Models (for safe deletion)
from app.models.student import Student
from app.models.instructor import Instructor
from app.models.administrator import Administrator
from app.models.data_analyst import DataAnalyst


# ============================================================
# DELETE USER (Senior Admin Only)
# ============================================================

def delete_user_service(db: Session, user_id: int):

    # --------------------------------------------------------
    # Fetch user
    # --------------------------------------------------------

    user = db.query(User).filter(
        User.user_id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # --------------------------------------------------------
    # DELETE ISA CHILD RECORDS
    # --------------------------------------------------------

    if user.student:
        db.delete(user.student)

    if user.instructor:
        db.delete(user.instructor)

    if user.administrator:
        db.delete(user.administrator)

    if user.analyst:
        db.delete(user.analyst)

    # --------------------------------------------------------
    # DELETE BASE USER
    # --------------------------------------------------------

    db.delete(user)
    db.commit()

    return {
        "message": f"User {user_id} deleted successfully"
    }


# ============================================================
# REMOVE INSTRUCTOR FROM COURSE
# ============================================================

def remove_instructor_service(
    db: Session,
    course_id: int,
    instructor_user_id: int
):

    teaching = db.query(Teaching).filter(
        Teaching.course_id == course_id,
        Teaching.instructor_user_id == instructor_user_id
    ).first()

    if not teaching:
        raise HTTPException(
            status_code=404,
            detail="Teaching assignment not found"
        )

    db.delete(teaching)
    db.commit()

    return {
        "message": "Instructor removed from course"
    }