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
    is_public: bool | None,
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
        review_text,
        is_public
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


def get_public_reviews_by_course_service(
    db: Session,
    course_id: int
):
    """Fetch public reviews for a course"""
    # Validate course exists
    course = course_repo.get_course_by_id(db, course_id)

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    return participation_repo.get_public_reviews_by_course(db, course_id)


def get_student_enrollments_service(
    db: Session,
    student_user_id: int
):
    """Fetch all enrollments for a student with course info"""
    # Validate user exists
    user = user_repo.get_user_by_id(db, student_user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    return participation_repo.get_student_enrollments(db, student_user_id)


def get_instructor_courses_service(
    db: Session,
    instructor_user_id: int
):
    """Fetch all courses taught by an instructor"""
    # Validate user exists and is an instructor
    user = user_repo.get_user_by_id(db, instructor_user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if user.role.lower() != "instructor":
        raise HTTPException(
            status_code=400,
            detail="User is not an instructor"
        )

    return participation_repo.get_courses_by_instructor(db, instructor_user_id)


# TOPIC PROGRESSION SERVICES

def update_topic_progress_service(
    db: Session,
    student_user_id: int,
    course_id: int,
    topic_id: int,
    current_user: dict
):
    """
    Update topic progression for a student.
    • Validates student is accessing their own data
    • Validates course and topic exist
    • Updates enrollment.current_topic
    • Returns updated enrollment
    """

    # --------------------------------------------------------
    # SELF CHECK
    # --------------------------------------------------------
    if current_user["role"] == Role.STUDENT.value:
        if current_user["user_id"] != student_user_id:
            raise HTTPException(
                status_code=403,
                detail="Students can update only their progress"
            )

    # Validate user exists and is a student
    user = user_repo.get_user_by_id(db, student_user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Student not found")
    if user.role.lower() != "student":
        raise HTTPException(status_code=400, detail="User is not a student")

    # Validate course exists
    course = course_repo.get_course_by_id(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Validate topic exists
    topic = course_repo.get_topic_by_id(db, topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    # Get enrollment
    enrollment = participation_repo.get_enrollment(db, student_user_id, course_id)
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")

    # Update current_topic
    return participation_repo.update_topic_progress(
        db,
        enrollment,
        topic_id
    )


def submit_assessment_service(
    db: Session,
    student_user_id: int,
    course_id: int,
    score: int | None,
    answers: list[str] | None,
    current_user: dict
):
    """
    Submit assessment and calculate grade.
    • Validates student is accessing their own data
    • Accepts either a precomputed percentage score or raw answers array
    • If answers provided: computes score using course.quiz_answer_key stored on Course
    • Maps score to grade (based on 15-question scale)
    • Updates enrollment.grade
    • Auto-completes course if grade != F
    • Returns score, grade, and completion status
    """

    # --------------------------------------------------------
    # SELF CHECK
    # --------------------------------------------------------
    if current_user["role"] == Role.STUDENT.value:
        if current_user["user_id"] != student_user_id:
            raise HTTPException(
                status_code=403,
                detail="Students can submit only their assessments"
            )

    # Validate user exists and is a student
    user = user_repo.get_user_by_id(db, student_user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Student not found")
    if user.role.lower() != "student":
        raise HTTPException(status_code=400, detail="User is not a student")

    # Validate course exists
    course = course_repo.get_course_by_id(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Get enrollment
    enrollment = participation_repo.get_enrollment(db, student_user_id, course_id)
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")

    # If answers provided, compute percent score using course.quiz_answer_key
    final_score = None
    if answers is not None:
        if not course.quiz_answer_key:
            raise HTTPException(status_code=400, detail="No answer key configured for this course")
        key = course.quiz_answer_key.strip()
        if len(key) == 0:
            raise HTTPException(status_code=400, detail="Answer key is empty")

        # Normalize key and compare
        key = key.upper()
        total = len(key)
        if len(answers) != total:
            raise HTTPException(status_code=400, detail=f"Answers length {len(answers)} does not match expected {total}")

        correct = 0
        for i, ans in enumerate(answers):
            if ans is None:
                continue
            if ans.upper() == key[i]:
                correct += 1

        # Convert to percentage (0-100)
        final_score = round((correct / total) * 100)
    elif score is not None:
        final_score = int(score)
    else:
        raise HTTPException(status_code=400, detail="Either 'score' or 'answers' must be provided")

    # Map score to grade
    grade = _map_score_to_grade(final_score)

    # Update grade
    participation_repo.update_grade(db, enrollment, grade)

    # Auto-complete if grade != F
    if grade != "F":
        participation_repo.update_completion(
            db,
            enrollment,
            "Completed",
            date.today()
        )

    # Return result
    return {
        "score": final_score,
        "grade": grade,
        "completion_status": "Completed" if grade != "F" else "Ongoing",
        "message": "Course completed successfully!" if grade != "F" else "Please attempt again to pass the course"
    }


def _map_score_to_grade(score: int) -> str:
    """
    Map score to grade.
    For 15-question quiz (converted to percentage):
    13–15 (86.67–100%) → A
    10–12 (66.67–86.66%) → B
    7–9 (46.67–66.66%) → C
    4–6 (26.67–46.66%) → D
    0–3 (0–26.66%) → F
    """
    if score >= 87:  # 13/15 = 86.67%
        return "A"
    elif score >= 67:  # 10/15 = 66.67%
        return "B"
    elif score >= 47:  # 7/15 = 46.67%
        return "C"
    elif score >= 27:  # 4/15 = 26.67%
        return "D"
    else:
        return "F"
