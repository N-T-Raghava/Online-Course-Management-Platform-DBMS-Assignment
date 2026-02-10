from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import date

from app.repositories import participation_repo
from app.repositories import user_repo
from app.repositories import course_repo

from app.models.teaching import Teaching

from app.core.roles import Role

# Import statistics service for updating stats on enrollment/teaching changes
from app.services.statistics_service import (
    update_course_statistics_service,
    update_student_statistics_service,
    update_instructor_statistics_service
)

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

    enrollment = participation_repo.create_enrollment(
        db,
        student_user_id,
        course_id
    )
    
    # Update statistics when new enrollment is created
    try:
        update_course_statistics_service(db, course_id)
        update_student_statistics_service(db, student_user_id)
        
        # Update statistics for all instructors teaching this course
        instructors = db.query(Teaching).filter(
            Teaching.course_id == course_id
        ).all()
        
        for teaching in instructors:
            try:
                update_instructor_statistics_service(db, teaching.instructor_user_id)
            except Exception:
                # Swallow individual instructor stats errors
                pass
                
    except Exception:
        # Swallow statistics update errors to not block enrollment
        pass
    
    return enrollment


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
    teaching = participation_repo.assign_instructor(
        db,
        instructor_user_id,
        course_id,
        assigned_date,
        role_in_course
    )
    
    # Update statistics when instructor is assigned
    try:
        update_instructor_statistics_service(db, instructor_user_id)
    except Exception:
        # Swallow statistics update errors to not block assignment
        pass
    
    return teaching


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


def rollback_topic_progress_service(
    db: Session,
    student_user_id: int,
    course_id: int,
    topic_id: int,
    current_user: dict
):
    """
    Rollback topic progression for a student (when unchecking a topic).
    • Validates student is accessing their own data
    • Validates course and topic exist
    • Sets enrollment.current_topic to previous topic (or None if first topic)
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

    # Find previous topic
    all_topics = course_repo.get_topics_by_course(db, course_id)
    
    # Filter out Final Assessment topic (already ordered by sequence_order from DB)
    regular_topics = [t for t in all_topics if t.name != "Final Assessment"]

    # Find index of current topic
    current_index = next((i for i, t in enumerate(regular_topics) if t.topic_id == topic_id), None)
    
    if current_index is None:
        raise HTTPException(status_code=400, detail="Topic not found in course")
    
    # Calculate previous topic_id
    if current_index == 0:
        # First topic - set to None
        previous_topic_id = None
    else:
        # Go to previous topic
        previous_topic_id = regular_topics[current_index - 1].topic_id

    # Update current_topic to previous topic
    return participation_repo.update_topic_progress(
        db,
        enrollment,
        previous_topic_id
    )


def reset_progress_service(
    db: Session,
    student_user_id: int,
    course_id: int,
    current_user: dict
):
    """
    Reset progress to first topic (when student fails quiz).
    • Validates student is accessing their own data
    • Validates course exists
    • Sets enrollment.current_topic to first topic
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

    # Get enrollment
    enrollment = participation_repo.get_enrollment(db, student_user_id, course_id)
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")

    # Get all topics and find the first one
    all_topics = course_repo.get_topics_by_course(db, course_id)
    
    # Filter out Final Assessment topic (already ordered by sequence_order from DB)
    regular_topics = [t for t in all_topics if t.name != "Final Assessment"]

    if not regular_topics:
        raise HTTPException(status_code=400, detail="No regular topics found in course")
    
    # Get first topic
    first_topic_id = regular_topics[0].topic_id

    # Update current_topic to first topic
    return participation_repo.update_topic_progress(
        db,
        enrollment,
        first_topic_id
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

    # If answers provided, prefer computing score using stored quiz questions
    final_score = None
    if answers is not None:
        # Try to load quiz and questions for this course
        quiz = None
        try:
            from app.repositories import quiz_repo
            quiz = quiz_repo.get_quiz_by_course(db, course_id)
        except Exception:
            quiz = None

        correct = 0
        total = 0

        if quiz:
            questions = quiz_repo.get_questions(db, quiz.quiz_id)
            total = len(questions)
            if total == 0:
                # fallback to answer key when there are no quiz_question rows
                questions = None
            else:
                if len(answers) != total:
                    raise HTTPException(status_code=400, detail=f"Answers length {len(answers)} does not match expected {total}")

                for i, q in enumerate(questions):
                    ans = answers[i]
                    if ans is None:
                        continue
                    if not q.correct_answer:
                        # treat missing correct_answer as non-matching
                        continue
                    if ans.upper() == q.correct_answer.upper():
                        correct += 1

        # If no quiz questions available, fall back to stored course answer key
        if not quiz or (quiz and (questions is None or len(questions) == 0)):
            if not course.quiz_answer_key:
                raise HTTPException(status_code=400, detail="No answer key configured for this course and no quiz questions available")
            key = course.quiz_answer_key.strip()
            if len(key) == 0:
                raise HTTPException(status_code=400, detail="Answer key is empty")

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
        if total == 0:
            raise HTTPException(status_code=400, detail="No questions/answer key available to grade answers")
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
    Map score (0-100) to grade using percentage thresholds.
    A: >= 85%
    B: >= 70%
    C: >= 50%
    D: >= 35%
    F: < 35%
    """
    if score >= 85:
        return "A"
    elif score >= 70:
        return "B"
    elif score >= 50:
        return "C"
    elif score >= 35:
        return "D"
    else:
        return "F"
