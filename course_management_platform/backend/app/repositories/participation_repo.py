from sqlalchemy.orm import Session
from datetime import date

from app.models.enrollment import Enrollment
from app.models.teaching import Teaching


# ENROLLMENT OPERATIONS
def create_enrollment(
    db: Session,
    student_user_id: int,
    course_id: int
) -> Enrollment:

    enrollment = Enrollment(
        student_user_id=student_user_id,
        course_id=course_id,
        enrollment_date=date.today(),
        status="Active",
        completion_status="In Progress"
    )

    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)

    return enrollment


def get_enrollment(
    db: Session,
    student_user_id: int,
    course_id: int
):
    return db.query(Enrollment).filter(
        Enrollment.student_user_id == student_user_id,
        Enrollment.course_id == course_id
    ).first()


def update_completion(
    db: Session,
    enrollment: Enrollment,
    completion_status: str,
    completion_date: date | None
):

    enrollment.completion_status = completion_status
    enrollment.completion_date = completion_date

    db.commit()
    db.refresh(enrollment)

    return enrollment


def update_rating(
    db: Session,
    enrollment: Enrollment,
    rating: int,
    review_text: str | None
):

    enrollment.rating = rating
    enrollment.review_text = review_text

    db.commit()
    db.refresh(enrollment)

    return enrollment


# TEACHING OPERATIONS
def assign_instructor(
    db: Session,
    instructor_user_id: int,
    course_id: int,
    assigned_date=None,
    role_in_course=None
) -> Teaching:

    teaching = Teaching(
        instructor_user_id=instructor_user_id,
        course_id=course_id,
        assigned_date=assigned_date,
        role_in_course=role_in_course
    )

    db.add(teaching)
    db.commit()
    db.refresh(teaching)

    return teaching


def get_teaching_assignment(
    db: Session,
    instructor_user_id: int,
    course_id: int
):
    return db.query(Teaching).filter(
        Teaching.instructor_user_id == instructor_user_id,
        Teaching.course_id == course_id
    ).first()


def get_instructors_by_course(
    db: Session,
    course_id: int
):
    return db.query(Teaching).filter(
        Teaching.course_id == course_id
    ).all()