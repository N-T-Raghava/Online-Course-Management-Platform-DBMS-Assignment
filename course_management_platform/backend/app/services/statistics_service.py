from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.repositories import statistics_repo
from app.models.statistics import Statistics
from app.models.student_statistics import StudentStatistics
from app.models.instructor_statistics import InstructorStatistics

# COURSE STATISTICS SERVICE

def update_course_statistics_service(db: Session, course_id: int):

    total, active, completed = (
        statistics_repo.get_course_enrollment_counts(
            db,
            course_id
        )
    )

    # Completion rate %
    completion_rate = 0

    if total > 0:
        completion_rate = (completed / total) * 100

    # Check if record exists
    stats = db.query(Statistics).filter(
        Statistics.course_id == course_id
    ).first()

    if not stats:
        stats = Statistics(course_id=course_id)
        db.add(stats)

    stats.total_enrollments = total
    stats.active_enrollments = active
    stats.completion_rate = round(completion_rate, 2)
    stats.average_completion_time = 0  # placeholder

    db.commit()
    db.refresh(stats)

    return stats


# STUDENT STATISTICS SERVICE

def update_student_statistics_service(
    db: Session,
    student_user_id: int
):

    total, completed, active = (
        statistics_repo.get_student_counts(
            db,
            student_user_id
        )
    )

    stats = db.query(StudentStatistics).filter(
        StudentStatistics.student_user_id == student_user_id
    ).first()

    if not stats:
        stats = StudentStatistics(
            student_user_id=student_user_id
        )
        db.add(stats)

    stats.total_enrollments = total
    stats.completed_courses = completed
    stats.active_courses = active

    db.commit()
    db.refresh(stats)

    return stats


# INSTRUCTOR STATISTICS SERVICE

def update_instructor_statistics_service(
    db: Session,
    instructor_user_id: int
):

    courses, students = (
        statistics_repo.get_instructor_counts(
            db,
            instructor_user_id
        )
    )

    stats = db.query(InstructorStatistics).filter(
        InstructorStatistics.instructor_user_id ==
        instructor_user_id
    ).first()

    if not stats:
        stats = InstructorStatistics(
            instructor_user_id=instructor_user_id
        )
        db.add(stats)

    stats.total_courses_taught = courses
    stats.total_students = students

    db.commit()
    db.refresh(stats)

    return stats


# FETCH ANALYTICS

def get_course_statistics_service(db: Session, course_id: int):

    stats = db.query(Statistics).filter(
        Statistics.course_id == course_id
    ).first()

    if not stats:
        raise HTTPException(
            status_code=404,
            detail="Course statistics not found"
        )

    return stats


def get_student_statistics_service(
    db: Session,
    student_user_id: int
):

    stats = db.query(StudentStatistics).filter(
        StudentStatistics.student_user_id ==
        student_user_id
    ).first()

    if not stats:
        raise HTTPException(
            status_code=404,
            detail="Student statistics not found"
        )

    return stats


def get_instructor_statistics_service(
    db: Session,
    instructor_user_id: int
):

    stats = db.query(InstructorStatistics).filter(
        InstructorStatistics.instructor_user_id ==
        instructor_user_id
    ).first()

    if not stats:
        raise HTTPException(
            status_code=404,
            detail="Instructor statistics not found"
        )

    return stats