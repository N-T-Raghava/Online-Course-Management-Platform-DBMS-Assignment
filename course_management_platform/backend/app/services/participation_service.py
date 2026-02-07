from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import date

from app.repositories import participation_repo
from app.repositories import user_repo
from app.repositories import course_repo

from app.core.roles import Role

def enroll_student_service(
    db: Session,
    student_user_id: int,
    course_id: int,
    current_user: dict
):

    # --------------------------------------------------------
    # SELF ENROLLMENT CHECK
    # --------------------------------------------------------

    if current_user["role"] == Role.STUDENT.value:
        if current_user["user_id"] != student_user_id:
            raise HTTPException(
                status_code=403,
                detail="Students can enroll only themselves"
            )

    # Admin override allowed → no block

    # Validate user exists
    user = user_repo.get_user_by_id(db, student_user_id)

    if not user:
        raise HTTPException(404, "User not found")

    if user.role.lower() != "student":
        raise HTTPException(400, "User is not a student")

    course = course_repo.get_course_by_id(db, course_id)

    if not course:
        raise HTTPException(404, "Course not found")

    existing = participation_repo.get_enrollment(
        db,
        student_user_id,
        course_id
    )

    if existing:
        raise HTTPException(400, "Student already enrolled")

    return participation_repo.create_enrollment(
        db,
        student_user_id,
        course_id
    )


# Completion Update
def update_completion_service(
    db: Session,
    student_user_id: int,
    course_id: int,
    completion_status: str,
    completion_date: date | None,
    current_user: dict
):

    # --------------------------------------------------------
    # SELF COMPLETION CHECK
    # --------------------------------------------------------

    if current_user["role"] == Role.STUDENT.value:
        if current_user["user_id"] != student_user_id:
            raise HTTPException(
                status_code=403,
                detail="Students can update only their completion"
            )

    enrollment = participation_repo.get_enrollment(
        db,
        student_user_id,
        course_id
    )

    if not enrollment:
        raise HTTPException(404, "Enrollment not found")

    return participation_repo.update_completion(
        db,
        enrollment,
        completion_status,
        completion_date
    )


# Rating Update
def rate_course_service(
    db: Session,
    student_user_id: int,
    course_id: int,
    rating: int,
    review_text: str | None,
    current_user: dict
):

    # --------------------------------------------------------
    # SELF RATING CHECK
    # --------------------------------------------------------

    if current_user["role"] == Role.STUDENT.value:
        if current_user["user_id"] != student_user_id:
            raise HTTPException(
                status_code=403,
                detail="Students can rate only their courses"
            )

    enrollment = participation_repo.get_enrollment(
        db,
        student_user_id,
        course_id
    )

    if not enrollment:
        raise HTTPException(404, "Enrollment not found")

    return participation_repo.update_rating(
        db,
        enrollment,
        rating,
        review_text
    )


# TEACHING SERVICES

def assign_instructor_service(
    db: Session,
    instructor_user_id: int,
    course_id: int,
    assigned_date,
    role_in_course
):

    # Validate user exists
    user = user_repo.get_user_by_id(
        db,
        instructor_user_id
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Validate role = Instructor
    if user.role.lower() != "instructor":
        raise HTTPException(
            status_code=400,
            detail="User is not an instructor"
        )

    # Validate course exists
    course = course_repo.get_course_by_id(
        db,
        course_id
    )

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    # Prevent duplicate assignment
    existing = participation_repo.get_teaching_assignment(
        db,
        instructor_user_id,
        course_id
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Instructor already assigned"
        )

    # Assign instructor
    return participation_repo.assign_instructor(
        db,
        instructor_user_id,
        course_id,
        assigned_date,
        role_in_course
    )