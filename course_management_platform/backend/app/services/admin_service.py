# backend/app/services/admin_service.py

from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

# Models
from app.models.user import User
from app.models.teaching import Teaching
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.instructor import Instructor

# ISA Models (for safe deletion)
from app.models.student import Student
from app.models.instructor import Instructor
from app.models.administrator import Administrator
from app.models.data_analyst import DataAnalyst


# ============================================================
# JUNIOR ADMIN: GET ALL COURSES (Approved + Pending)
# ============================================================

def get_all_courses_admin_service(db: Session):
    """Get all courses (both approved and pending) for admin view"""
    courses = db.query(Course).all()
    
    result = []
    for course in courses:
        # Fetch instructor from Teaching table (not course.instructor)
        instructor_name = "Unknown"
        teaching = db.query(Teaching).filter(
            Teaching.course_id == course.course_id
        ).first()
        if teaching and teaching.instructor_user_id:
            instructor = db.query(User).filter(
                User.user_id == teaching.instructor_user_id
            ).first()
            if instructor:
                instructor_name = f"{instructor.name}"
        
        result.append({
            "course_id": course.course_id,
            "title": course.title,
            "course_name": course.title,
            "category": course.category,
            "level": course.level,
            "difficulty_level": course.level,
            "approval_status": course.approval_status,
            "created_by": course.created_by,
            "instructor_name": instructor_name,
            "start_date": course.start_date,
            "duration": course.duration,
            "duration_in_weeks": course.duration,
        })
    
    return result


# ============================================================
# JUNIOR ADMIN: GET PENDING COURSES ONLY
# ============================================================

def get_pending_courses_service(db: Session):
    """Get only pending courses for admin review"""
    courses = db.query(Course).filter(
        Course.approval_status == 'Pending'
    ).all()
    
    result = []
    for course in courses:
        # Fetch instructor from Teaching table (not course.instructor)
        instructor_name = "Unknown"
        teaching = db.query(Teaching).filter(
            Teaching.course_id == course.course_id
        ).first()
        if teaching and teaching.instructor_user_id:
            instructor = db.query(User).filter(
                User.user_id == teaching.instructor_user_id
            ).first()
            if instructor:
                instructor_name = f"{instructor.first_name} {instructor.last_name}"
        
        result.append({
            "course_id": course.course_id,
            "title": course.title,
            "course_name": course.title,
            "description": course.description,
            "category": course.category,
            "level": course.level,
            "difficulty_level": course.level,
            "language": course.language,
            "duration": course.duration,
            "duration_in_weeks": course.duration,
            "created_by": course.created_by,
            "instructor_name": instructor_name,
            "start_date": course.start_date,
        })
    
    return result


# ============================================================
# JUNIOR ADMIN: GET COURSE DETAILS
# ============================================================

def get_course_details_admin_service(db: Session, course_id: int):
    """Get detailed course information for admin view"""
    course = db.query(Course).filter(
        Course.course_id == course_id
    ).first()
    
    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )
    
    # Fetch instructor from Teaching table
    instructor_name = "Unknown"
    instructor_email = "N/A"
    instructor_user_id = None
    teaching = db.query(Teaching).filter(
        Teaching.course_id == course_id
    ).first()
    if teaching and teaching.instructor_user_id:
        instructor = db.query(User).filter(
            User.user_id == teaching.instructor_user_id
        ).first()
        if instructor:
            instructor_name = f"{instructor.name}"
            instructor_email = instructor.email
            instructor_user_id = instructor.user_id
    
    return {
        "course_id": course.course_id,
        "title": course.title,
        "course_name": course.title,
        "description": course.description,
        "category": course.category,
        "level": course.level,
        "difficulty_level": course.level,
        "language": course.language,
        "duration": course.duration,
        "duration_in_weeks": course.duration,
        "start_date": course.start_date,
        "approval_status": course.approval_status,
        "created_by": course.created_by,
        "instructor_name": instructor_name,
        "instructor_email": instructor_email,
        "instructor_user_id": instructor_user_id,
        "approved_by": course.approved_by,
        "approved_at": course.approved_at,
        "university_id": course.university_id,
    }


# ============================================================
# JUNIOR ADMIN: GET COURSE STATISTICS
# ============================================================

def get_course_statistics_admin_service(db: Session, course_id: int):
    """Get course enrollment and completion statistics"""
    course = db.query(Course).filter(
        Course.course_id == course_id
    ).first()
    
    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )
    
    # Get enrollment statistics
    enrollments = db.query(Enrollment).filter(
        Enrollment.course_id == course_id
    ).all()
    
    total_enrolled = len(enrollments)
    completed = sum(1 for e in enrollments if e.completion_status == 'Completed')
    pending = sum(1 for e in enrollments if e.completion_status != 'Completed')
    
    completion_rate = 0
    if total_enrolled > 0:
        completion_rate = round((completed / total_enrolled) * 100, 2)
    
    # Get average rating
    ratings = [e.rating for e in enrollments if e.rating is not None]
    avg_rating = round(sum(ratings) / len(ratings), 2) if ratings else 0
    
    return {
        "course_id": course_id,
        "enrolled_count": total_enrolled,
        "completed_count": completed,
        "in_progress_count": pending,
        "completion_rate": completion_rate,
        "average_rating": avg_rating,
        "total_ratings": len(ratings),
    }


# ============================================================
# JUNIOR ADMIN: GET COURSE RATINGS AND REVIEWS
# ============================================================

def get_course_ratings_admin_service(db: Session, course_id: int):
    """Get all ratings and public reviews for a course"""
    course = db.query(Course).filter(
        Course.course_id == course_id
    ).first()
    
    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )
    
    # Get all enrollments with ratings/reviews
    enrollments = db.query(Enrollment).filter(
        Enrollment.course_id == course_id
    ).all()
    
    ratings_data = []
    for enrollment in enrollments:
        if enrollment.rating is not None or enrollment.review_text is not None:
            # Resolve student user from student_user_id (Enrollment has no relationship property)
            student_name = "Anonymous"
            student_user = db.query(User).filter(User.user_id == enrollment.student_user_id).first()
            if student_user:
                student_name = f"{student_user.name}"
            
            ratings_data.append({
                "student_id": enrollment.student_user_id,
                "student_name": student_name,
                "rating": enrollment.rating,
                "review_text": enrollment.review_text,
                "is_review_public": enrollment.is_review_public,
                "rated_at": enrollment.rated_at,
            })
    
    return ratings_data


# ============================================================
# JUNIOR ADMIN: APPROVE COURSE
# ============================================================

def approve_course_service(db: Session, course_id: int, admin_user_id: int):
    """
    Approve a pending course (Junior Admin privilege).
    When approved, automatically assigns the course creator as the Lead Instructor.
    """
    course = db.query(Course).filter(
        Course.course_id == course_id
    ).first()
    
    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )
    
    if course.approval_status == 'Approved':
        raise HTTPException(
            status_code=400,
            detail="Course is already approved"
        )
    
    course.approval_status = 'Approved'
    course.approved_by = admin_user_id
    course.approved_at = datetime.now()
    
    db.commit()
    
    # ================================================================
    # AUTO-ASSIGN INSTRUCTOR TO COURSE
    # ================================================================
    # If the course was created by an instructor (created_by field),
    # automatically assign them as the course instructor
    
    instructor_assigned = False
    if course.created_by:
        # Check if instructor is already assigned to this course
        existing_teaching = db.query(Teaching).filter(
            Teaching.course_id == course_id,
            Teaching.instructor_user_id == course.created_by
        ).first()
        
        # Only create if not already assigned
        if not existing_teaching:
            teaching = Teaching(
                course_id=course_id,
                instructor_user_id=course.created_by,
                assigned_date=datetime.now().date(),
                role_in_course="Lead Instructor"
            )
            db.add(teaching)
            db.commit()
            instructor_assigned = True
    
    db.refresh(course)
    
    return {
        "message": "Course approved successfully",
        "course_id": course.course_id,
        "status": course.approval_status,
        "instructor_assigned": instructor_assigned
    }


# ============================================================
# JUNIOR ADMIN: REJECT COURSE
# ============================================================

def reject_course_service(db: Session, course_id: int, reason: str = None):
    """Reject a pending course (Junior Admin privilege)"""
    course = db.query(Course).filter(
        Course.course_id == course_id
    ).first()
    
    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )
    
    if course.approval_status == 'Approved':
        raise HTTPException(
            status_code=400,
            detail="Cannot reject an already approved course"
        )
    
    course.approval_status = 'Rejected'
    
    db.commit()
    db.refresh(course)
    
    return {
        "message": "Course rejected",
        "course_id": course.course_id,
        "status": course.approval_status,
        "reason": reason
    }


# ============================================================
# SENIOR ADMIN: DELETE COURSE REQUEST
# ============================================================

def delete_course_request_service(db: Session, course_id: int):
    """Delete a pending course request (Senior Admin Only)"""
    course = db.query(Course).filter(
        Course.course_id == course_id
    ).first()
    
    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )
    
    if course.approval_status == 'Approved':
        raise HTTPException(
            status_code=400,
            detail="Cannot delete an approved course"
        )
    
    course_id_deleted = course.course_id
    db.delete(course)
    db.commit()
    
    return {
        "message": "Course request deleted successfully",
        "course_id": course_id_deleted
    }


# ============================================================
# SENIOR ADMIN: DELETE PUBLIC RATING
# ============================================================

def delete_public_rating_service(db: Session, student_user_id: int, course_id: int):
    """Delete a public rating/review (Senior Admin Only)"""
    enrollment = db.query(Enrollment).filter(
        Enrollment.student_user_id == student_user_id,
        Enrollment.course_id == course_id
    ).first()
    
    if not enrollment:
        raise HTTPException(
            status_code=404,
            detail="Enrollment not found"
        )
    
    if not enrollment.is_review_public:
        raise HTTPException(
            status_code=400,
            detail="This rating is not public"
        )
    
    enrollment.rating = None
    enrollment.review_text = None
    enrollment.is_review_public = False
    
    db.commit()
    db.refresh(enrollment)
    
    return {
        "message": "Public rating deleted successfully",
        "student_id": student_user_id,
        "course_id": course_id
    }




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


# ============================================================
# GET STUDENTS ENROLLED IN COURSE
# ============================================================

def get_course_students_service(db: Session, course_id: int):
    """Get all students enrolled in a specific course"""
    course = db.query(Course).filter(
        Course.course_id == course_id
    ).first()
    
    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )
    
    # Query all enrollments for this course
    enrollments = db.query(Enrollment).filter(
        Enrollment.course_id == course_id
    ).all()
    
    students_list = []
    for enrollment in enrollments:
        student = db.query(User).filter(
            User.user_id == enrollment.student_user_id
        ).first()
        
        if student:
            students_list.append({
                "student_user_id": student.user_id,
                "student_name": f"{student.name}",
                "student_email": student.email,
                "completion_status": enrollment.completion_status,
                "enrollment_date": enrollment.enrollment_date,
                "rating": enrollment.rating,
                "review_text": enrollment.review_text,
                "is_review_public": enrollment.is_review_public,
                "grade": enrollment.grade,
            })
    
    return {
        "course_id": course_id,
        "course_name": course.title,
        "total_students": len(students_list),
        "students": students_list
    }


# ============================================================
# GET STUDENT PROFILE WITH COURSES AND RATINGS
# ============================================================

def get_student_profile_service(db: Session, student_user_id: int):
    """Get student profile with all courses and ratings"""
    student_user = db.query(User).filter(
        User.user_id == student_user_id
    ).first()
    
    if not student_user:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )
    
    # Get student details
    student = db.query(Student).filter(
        Student.user_id == student_user_id
    ).first()
    
    # Get all enrollments
    enrollments = db.query(Enrollment).filter(
        Enrollment.student_user_id == student_user_id
    ).all()
    
    # Build courses list
    courses_list = []
    ratings_list = []
    
    for enrollment in enrollments:
        course = db.query(Course).filter(
            Course.course_id == enrollment.course_id
        ).first()
        
        if course:
            courses_list.append({
                "course_id": course.course_id,
                "course_name": course.title,
                "category": course.category,
                "level": course.level,
                "completion_status": enrollment.completion_status,
                "enrollment_date": enrollment.enrollment_date,
                "completion_date": enrollment.completion_date,
                "grade": enrollment.grade,
            })
            
            # Add rating if exists
            if enrollment.rating is not None:
                ratings_list.append({
                    "course_id": course.course_id,
                    "course_name": course.title,
                    "rating": enrollment.rating,
                    "review_text": enrollment.review_text,
                    "is_review_public": enrollment.is_review_public,
                    "rated_at": enrollment.rated_at,
                })
    
    profile_data = {
        "student_user_id": student_user.user_id,
        "student_name": f"{student_user.name}",
        "student_email": student_user.email,
        "date_of_birth": student.date_of_birth if student else None,
        "country": student.country if student else None,
        "gender": student.gender if student else None,
        "education_level": student.education_level if student else None,
        "total_courses": len(courses_list),
        "courses": courses_list,
        "total_ratings": len(ratings_list),
        "ratings": ratings_list,
    }
    
    return profile_data