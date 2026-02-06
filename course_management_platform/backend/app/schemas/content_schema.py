from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


# Upload Content
class ContentCreate(BaseModel):
    title: str = Field(..., max_length=150)
    content_type: Optional[str]
    file_url: str

    course_id: int
    topic_id: Optional[int]
    instructor_user_id: Optional[int]

# Content Response
class ContentResponse(BaseModel):
    content_id: int
    title: str
    content_type: Optional[str]
    file_url: str
    course_id: int
    topic_id: Optional[int]

    class Config:
        orm_mode = True