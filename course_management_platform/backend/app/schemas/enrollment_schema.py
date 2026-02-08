from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime

# Enroll Student
class EnrollmentCreate(BaseModel):
    student_user_id: int
    course_id: int


# Completion Update
class CompletionUpdate(BaseModel):
    completion_status: str = Field(..., example="Completed")
    completion_date: Optional[date]


# Topic Progress Update
class ProgressUpdate(BaseModel):
    """Update topic progression for a student"""
    topic_id: int

    class Config:
        orm_mode = True


# Rating Schema
class RatingUpdate(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    review_text: Optional[str]


# Public Review Response (displayed on course detail page)
class PublicReviewResponse(BaseModel):
    """Public review displayed on course detail page"""
    student_name: str
    rating: int
    review_text: Optional[str]
    rated_at: Optional[datetime]

    class Config:
        orm_mode = True


# Student Enrollment Response
class StudentEnrollmentResponse(BaseModel):
    """Student enrollment with course details"""
    course_id: int
    course_title: str
    category: Optional[str]
    level: Optional[str]
    duration: Optional[int]
    enrollment_date: date
    completion_status: Optional[str]
    status: Optional[str]
    grade: Optional[str]
    rating: Optional[int]
    completion_date: Optional[date]
    current_topic: Optional[int]

    class Config:
        orm_mode = True


# Assessment Submission
class AssessmentSubmission(BaseModel):
    """Submit assessment with score"""
    score: int = Field(..., ge=0, le=100)

    class Config:
        orm_mode = True