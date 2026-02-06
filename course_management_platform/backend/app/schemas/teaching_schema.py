from pydantic import BaseModel
from typing import Optional
from datetime import date


# Assign Instructor
class TeachingAssign(BaseModel):
    instructor_user_id: int
    course_id: int
    assigned_date: Optional[date]
    role_in_course: Optional[str]