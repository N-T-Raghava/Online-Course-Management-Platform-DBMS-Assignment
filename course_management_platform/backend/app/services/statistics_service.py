from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.repositories import statistics_repo
from app.models.statistics import Statistics
from app.models.student_statistics import StudentStatistics
from app.models.instructor_statistics import InstructorStatistics
from app.models.student import Student
from app.models.instructor import Instructor
from app.models.student import Student
from app.models.course import Course
from app.models.enrollment import Enrollment

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

    # Ensure the user has a Student record before computing stats
    student = db.query(Student).filter(
        Student.user_id == student_user_id
    ).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

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

    # Ensure the user has an Instructor record before computing stats
    instr = db.query(Instructor).filter(
        Instructor.user_id == instructor_user_id
    ).first()

    if not instr:
        raise HTTPException(status_code=404, detail="Instructor not found")

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

    # Try to fetch precomputed stats row (may exist), but also compute a few live values
    stats = db.query(Statistics).filter(
        Statistics.course_id == course_id
    ).first()

    # Live calculations from enrollments
    from sqlalchemy import func
    total = db.query(func.count()).filter(Enrollment.course_id == course_id).scalar() or 0
    completed = db.query(func.count()).filter(
        Enrollment.course_id == course_id,
        Enrollment.completion_status == 'Completed'
    ).scalar() or 0
    active = db.query(func.count()).filter(
        Enrollment.course_id == course_id,
        Enrollment.completion_status != 'Completed'
    ).scalar() or 0

    avg_rating = db.query(func.avg(Enrollment.rating)).filter(
        Enrollment.course_id == course_id,
        Enrollment.rating.isnot(None)
    ).scalar()
    # avg_rating may be None if no ratings
    if avg_rating is not None:
        avg_rating = round(float(avg_rating), 2)

    # If no precomputed stats exist, compute basic completion rate
    if not stats:
        completion_rate = round((completed / total * 100), 2) if total > 0 else 0
        return {
            'total_enrollments': total,
            'active_enrollments': active,
            'completion_rate': completion_rate,
            'average_completion_time': None,
            'completed_students': completed,
            'active_students': active,
            'pending_students': total - completed,
            'average_rating': avg_rating if avg_rating is not None else 0
        }

    # Build response merging stored stats and live values
    response = {
        'total_enrollments': stats.total_enrollments or total,
        'active_enrollments': stats.active_enrollments or active,
        'completion_rate': float(stats.completion_rate) if stats.completion_rate is not None else (round((completed / total * 100), 2) if total > 0 else 0),
        'average_completion_time': stats.average_completion_time,
        'completed_students': completed,
        'active_students': active,
        'pending_students': total - completed,
        'average_rating': avg_rating if avg_rating is not None else 0
    }

    return response


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


# ---------------- Batch Recompute Helpers -----------------
def recompute_all_students_service(db: Session):
    """Recompute statistics for all students that have Student records."""
    student_ids = [s.user_id for s in db.query(Student).all()]
    updated = 0
    errors = []
    for sid in student_ids:
        try:
            update_student_statistics_service(db, sid)
            updated += 1
        except Exception as e:
            # collect errors but continue
            errors.append({"student_user_id": sid, "error": str(e)})

    return {"updated": updated, "errors": errors}


def recompute_all_instructors_service(db: Session):
    """Recompute statistics for all instructors that have Instructor records."""
    instructor_ids = [i.user_id for i in db.query(Instructor).all()]
    updated = 0
    errors = []
    for iid in instructor_ids:
        try:
            update_instructor_statistics_service(db, iid)
            updated += 1
        except Exception as e:
            errors.append({"instructor_user_id": iid, "error": str(e)})

    return {"updated": updated, "errors": errors}


def recompute_all_courses_service(db: Session):
    """Recompute statistics for all courses."""
    course_ids = [c.course_id for c in db.query(Course).all()]
    updated = 0
    errors = []
    for cid in course_ids:
        try:
            update_course_statistics_service(db, cid)
            updated += 1
        except Exception as e:
            errors.append({"course_id": cid, "error": str(e)})

    return {"updated": updated, "errors": errors}


def recompute_platform_service(db: Session):
    """Run all recompute tasks for platform (students, instructors, courses)."""
    res = {
        "students": recompute_all_students_service(db),
        "instructors": recompute_all_instructors_service(db),
        "courses": recompute_all_courses_service(db)
    }
    return res