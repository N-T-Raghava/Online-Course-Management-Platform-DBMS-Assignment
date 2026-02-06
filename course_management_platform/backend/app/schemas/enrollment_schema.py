from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

# Enroll Student
class EnrollmentCreate(BaseModel):
    student_user_id: int
    course_id: int


# Completion Update
class CompletionUpdate(BaseModel):
    completion_status: str = Field(..., example="Completed")
    completion_date: Optional[date]


# Rating Schema
class RatingUpdate(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    review_text: Optional[str]