from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.topic_schema import (
    TopicCreate,
    TopicResponse,
    CourseTopicMap,
    CourseTopicCreateOrMap
)
from app.services.course_service import (
    create_topic_service,
    get_all_topics_service,
    map_topic_to_course_service,
    get_topics_by_course_service,
    create_and_map_topic_service,
    delete_topic_from_course_service
)
from app.core.role_guards import require_role
from app.core.roles import Role
from app.repositories import course_repo

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
def map_or_create_topic_to_course(
    course_id: int,
    payload: dict = Body(...),
    db: Session = Depends(get_db)
):
    """
    Create a new topic and map it, OR map an existing topic to a course.

    Accepts a flexible JSON payload. Examples:
    - { "name": "New Topic", "description": "..." }
    - { "topic_id": 12, "sequence_order": 2 }
    """
    name = payload.get('name')
    description = payload.get('description')
    topic_id = payload.get('topic_id')
    sequence_order = payload.get('sequence_order')

    # If creating by name
    if name:
        return create_and_map_topic_service(
            db,
            course_id,
            name,
            description
        )

    # If mapping existing topic
    if topic_id:
        return map_topic_to_course_service(
            db,
            course_id,
            topic_id,
            sequence_order
        )

    from fastapi import HTTPException
    raise HTTPException(
        status_code=400,
        detail="Either 'name' (to create) or 'topic_id' (to map) must be provided"
    )



@router.get("/courses/{course_id}/topics", response_model=list[TopicResponse])
def get_topics_by_course(
    course_id: int,
    db: Session = Depends(get_db)
):
    return get_topics_by_course_service(db, course_id)


@router.delete("/courses/{course_id}/topics/{topic_id}")
def delete_topic_from_course(
    course_id: int,
    topic_id: int,
    db: Session = Depends(get_db),
    instructor = Depends(require_role([Role.INSTRUCTOR]))
):
    """Delete a topic mapping from a course (instructor-only)."""
    # Helpful debug: print current mappings before delete
    try:
        from app.repositories.course_repo import get_course_topic_mappings
        mappings = get_course_topic_mappings(db, course_id)
        print(f"DEBUG: current mappings for course {course_id}: {[{'topic_id': m.topic_id, 'sequence_order': m.sequence_order} for m in mappings]}")
    except Exception:
        pass

    return delete_topic_from_course_service(db, course_id, topic_id)


@router.get('/courses/{course_id}/topics/mappings')
def get_course_topic_mappings_route(
    course_id: int,
    db: Session = Depends(get_db)
):
    """Return raw course-topic mappings (topic_id, sequence_order) for debugging and ordering checks."""
    mappings = course_repo.get_course_topic_mappings(db, course_id)
    return [
        { 'topic_id': m.topic_id, 'sequence_order': m.sequence_order }
        for m in mappings
    ]