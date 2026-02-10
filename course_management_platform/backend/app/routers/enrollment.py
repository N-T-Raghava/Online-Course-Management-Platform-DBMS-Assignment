from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.enrollment_schema import (
    EnrollmentCreate,
    CompletionUpdate,
    RatingUpdate,
    PublicReviewResponse,
    StudentEnrollmentResponse,
    ProgressUpdate,
    AssessmentSubmission
)
from app.services.participation_service import (
    enroll_student_service,
    update_completion_service,
    rate_course_service,
    get_public_reviews_by_course_service,
    get_student_enrollments_service,
    update_topic_progress_service,
    rollback_topic_progress_service,
    reset_progress_service,
    submit_assessment_service
)

# 🔐 Auth Dependency (JWT Payload)
from app.core.dependencies import get_current_user

# Router Config
router = APIRouter(
    prefix="/enrollments",
    tags=["Participation - Enrollment"]
)

# ENROLL STUDENT
@router.post("/")
def enroll_student(
    payload: EnrollmentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return enroll_student_service(
        db,
        payload.student_user_id,
        payload.course_id,
        current_user
    )

# UPDATE COMPLETION
@router.put("/complete/{student_user_id}/{course_id}")
def update_completion(
    student_user_id: int,
    course_id: int,
    payload: CompletionUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return update_completion_service(
        db,
        student_user_id,
        course_id,
        payload.completion_status,
        payload.completion_date,
        current_user
    )

# RATE COURSE
@router.post("/rate/{student_user_id}/{course_id}")
def rate_course(
    student_user_id: int,
    course_id: int,
    payload: RatingUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return rate_course_service(
        db,
        student_user_id,
        course_id,
        payload.rating,
        payload.review_text,
        payload.is_public,
        current_user
    )

# GET PUBLIC REVIEWS FOR A COURSE
@router.get("/reviews/{course_id}", response_model=list[PublicReviewResponse])
def get_public_reviews(
    course_id: int,
    db: Session = Depends(get_db)
):
    return get_public_reviews_by_course_service(db, course_id)

# GET STUDENT ENROLLMENTS
@router.get("/student/{student_user_id}", response_model=list[StudentEnrollmentResponse])
def get_student_enrollments(
    student_user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return get_student_enrollments_service(db, student_user_id)

# UPDATE TOPIC PROGRESS
@router.put("/progress/{student_user_id}/{course_id}/{topic_id}")
def update_topic_progress(
    student_user_id: int,
    course_id: int,
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return update_topic_progress_service(
        db,
        student_user_id,
        course_id,
        topic_id,
        current_user
    )

# ROLLBACK TOPIC PROGRESS (when unchecking a topic)
@router.put("/rollback/{student_user_id}/{course_id}/{topic_id}")
def rollback_topic_progress(
    student_user_id: int,
    course_id: int,
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return rollback_topic_progress_service(
        db,
        student_user_id,
        course_id,
        topic_id,
        current_user
    )


# RESET PROGRESS TO FIRST TOPIC (when quiz is failed)
@router.put("/reset/{student_user_id}/{course_id}")
def reset_progress(
    student_user_id: int,
    course_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return reset_progress_service(
        db,
        student_user_id,
        course_id,
        current_user
    )


# SUBMIT ASSESSMENT
# Accepts either precomputed score (0-100%) OR answers array
# If answers provided: server validates against course.quiz_answer_key
@router.post("/assessment/{student_user_id}/{course_id}")
def submit_assessment(
    student_user_id: int,
    course_id: int,
    payload: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    score = payload.get('score')
    answers = payload.get('answers')
    return submit_assessment_service(
        db,
        student_user_id,
        course_id,
        score,
        answers,
        current_user
    )
