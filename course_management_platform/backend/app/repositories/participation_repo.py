from sqlalchemy.orm import Session
from datetime import date

from app.models.enrollment import Enrollment
from app.models.teaching import Teaching
from app.models.user import User


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


def get_public_reviews_by_course(
    db: Session,
    course_id: int
):
    """Fetch all public reviews for a course with student names"""
    return db.query(
        User.name.label("student_name"),
        Enrollment.rating,
        Enrollment.review_text,
        Enrollment.rated_at
    ).join(
        User,
        User.user_id == Enrollment.student_user_id
    ).filter(
        Enrollment.course_id == course_id,
        Enrollment.is_review_public == True,
        Enrollment.rating.isnot(None)
    ).order_by(
        Enrollment.rated_at.desc()
    ).all()


def get_student_enrollments(
    db: Session,
    student_user_id: int
):
    """Fetch all enrollments for a student with course details"""
    from app.models.course import Course
    
    enrollments = db.query(Enrollment, Course).join(
        Course,
        Course.course_id == Enrollment.course_id
    ).filter(
        Enrollment.student_user_id == student_user_id
    ).order_by(
        Enrollment.enrollment_date.desc()
    ).all()
    
    # Transform to dict format for serialization
    result = []
    for enrollment, course in enrollments:
        result.append({
            'course_id': course.course_id,
            'course_title': course.title,
            'category': course.category,
            'level': course.level,
            'duration': course.duration,
            'enrollment_date': enrollment.enrollment_date,
            'completion_status': enrollment.completion_status,
            'status': enrollment.status,
            'grade': enrollment.grade,
            'rating': enrollment.rating,
            'completion_date': enrollment.completion_date
        })
    
    return result


def get_courses_by_instructor(
    db: Session,
    instructor_user_id: int
):
    """Fetch all courses taught by an instructor"""
    from app.models.course import Course
    
    teachings = db.query(Teaching, Course).join(
        Course,
        Course.course_id == Teaching.course_id
    ).filter(
        Teaching.instructor_user_id == instructor_user_id
    ).order_by(
        Course.title.asc()
    ).all()
    
    # Transform to dict format for serialization
    result = []
    for teaching, course in teachings:
        # Get enrollment count for the course
        enrollment_count = db.query(Enrollment).filter(
            Enrollment.course_id == course.course_id
        ).count()
        
        # Get completion count
        completion_count = db.query(Enrollment).filter(
            Enrollment.course_id == course.course_id,
            Enrollment.completion_status == "Completed"
        ).count()
        
        result.append({
            'course_id': course.course_id,
            'course_title': course.title,
            'category': course.category,
            'level': course.level,
            'duration': course.duration,
            'description': course.description,
            'role_in_course': teaching.role_in_course,
            'assigned_date': teaching.assigned_date,
            'enrollment_count': enrollment_count,
            'completion_count': completion_count
        })
    
    return result