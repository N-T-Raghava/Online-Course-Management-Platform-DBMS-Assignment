from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.topic_schema import (
    TopicCreate,
    TopicResponse,
    CourseTopicMap
)
from app.services.course_service import (
    create_topic_service,
    get_all_topics_service,
    map_topic_to_course_service,
    get_topics_by_course_service
)

# Router Config
router = APIRouter(
    prefix="",
    tags=["Academic - Topics"]
)


# TOPIC ROUTES
@router.post(
    "/topics",
    response_model=TopicResponse
)
def create_topic(
    payload: TopicCreate,
    db: Session = Depends(get_db)
):
    return create_topic_service(db, payload)


@router.get(
    "/topics",
    response_model=list[TopicResponse]
)
def get_topics(
    db: Session = Depends(get_db)
):
    return get_all_topics_service(db)


# COURSE ↔ TOPIC MAPPING
@router.post("/courses/{course_id}/topics")
def map_topic_to_course(
    course_id: int,
    payload: CourseTopicMap,
    db: Session = Depends(get_db)
):
    return map_topic_to_course_service(
        db,
        course_id,
        payload.topic_id,
        payload.sequence_order
    )


@router.get("/courses/{course_id}/topics", response_model=list[TopicResponse])
def get_topics_by_course(
    course_id: int,
    db: Session = Depends(get_db)
):
    return get_topics_by_course_service(db, course_id)