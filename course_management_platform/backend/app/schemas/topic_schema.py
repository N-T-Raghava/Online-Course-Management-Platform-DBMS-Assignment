from pydantic import BaseModel, Field
from typing import Optional

# Topic Create
class TopicCreate(BaseModel):
    name: str = Field(..., max_length=150)
    description: Optional[str]

# Topic Response
class TopicResponse(BaseModel):
    topic_id: int
    name: str
    description: Optional[str]

    class Config:
        orm_mode = True

# Course Topic Mapping
class CourseTopicMap(BaseModel):
    course_id: int
    topic_id: int
    sequence_order: Optional[int]


# Combined: Can be either existing topic ID or new topic creation
class CourseTopicCreateOrMap(BaseModel):
    """Handles both creating a new topic and mapping it, or mapping an existing topic"""
    name: Optional[str] = None  # For creating new topic
    description: Optional[str] = None  # For creating new topic
    topic_id: Optional[int] = None  # For mapping existing topic
    sequence_order: Optional[int] = None
