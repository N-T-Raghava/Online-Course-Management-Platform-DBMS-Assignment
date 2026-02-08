from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

# University Schemas
class UniversityCreate(BaseModel):
    name: str = Field(..., max_length=150)
    region: Optional[str]
    country: Optional[str]
    website: Optional[str]


class UniversityResponse(BaseModel):
    university_id: int
    name: str
    region: Optional[str]
    country: Optional[str]
    website: Optional[str]

    class Config:
        orm_mode = True

# Course Schemas
class CourseCreate(BaseModel):
    title: str = Field(..., max_length=150)
    description: Optional[str]
    category: Optional[str]
    level: Optional[str]
    language: Optional[str]
    start_date: Optional[date]
    duration: Optional[int]
    university_id: Optional[int]
    quiz_answer_key: Optional[str] = Field(None, max_length=15)  # Format: "ABCDACBDABCDABC"


class CourseResponse(BaseModel):
    course_id: int
    title: str
    description: Optional[str]
    category: Optional[str]
    level: Optional[str]
    language: Optional[str]
    duration: Optional[int]
    quiz_answer_key: Optional[str]

    class Config:
        orm_mode = True