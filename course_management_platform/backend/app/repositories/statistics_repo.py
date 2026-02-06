from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.enrollment import Enrollment
from app.models.teaching import Teaching
from app.models.statistics import Statistics
from app.models.student_statistics import StudentStatistics
from app.models.instructor_statistics import InstructorStatistics


# COURSE STATISTICS CALCULATIONS

def get_course_enrollment_counts(db: Session, course_id: int):

    total = db.query(func.count()).filter(
        Enrollment.course_id == course_id
    ).scalar()

    active = db.query(func.count()).filter(
        Enrollment.course_id == course_id,
        Enrollment.completion_status != "Completed"
    ).scalar()

    completed = db.query(func.count()).filter(
        Enrollment.course_id == course_id,
        Enrollment.completion_status == "Completed"
    ).scalar()

    return total, active, completed

# STUDENT STATISTICS

def get_student_counts(db: Session, student_user_id: int):

    total = db.query(func.count()).filter(
        Enrollment.student_user_id == student_user_id
    ).scalar()

    completed = db.query(func.count()).filter(
        Enrollment.student_user_id == student_user_id,
        Enrollment.completion_status == "Completed"
    ).scalar()

    active = total - completed

    return total, completed, active


# INSTRUCTOR STATISTICS

def get_instructor_counts(db: Session, instructor_user_id: int):

    courses = db.query(func.count()).filter(
        Teaching.instructor_user_id == instructor_user_id
    ).scalar()

    students = db.query(func.count()).join(
        Teaching,
        Teaching.course_id == Enrollment.course_id
    ).filter(
        Teaching.instructor_user_id == instructor_user_id
    ).scalar()

    return courses, students