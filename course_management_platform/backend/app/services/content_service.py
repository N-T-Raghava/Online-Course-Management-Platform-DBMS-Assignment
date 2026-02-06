from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.repositories import content_repo
from app.repositories import course_repo
from app.repositories import user_repo
from app.models.topic import Topic


# UPLOAD CONTENT

def upload_content_service(db: Session, payload):

    # Validate course
    course = course_repo.get_course_by_id(
        db,
        payload.course_id
    )

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    # Validate instructor if provided
    if payload.instructor_user_id:

        user = user_repo.get_user_by_id(
            db,
            payload.instructor_user_id
        )

        if not user or user.role.lower() != "instructor":
            raise HTTPException(
                status_code=400,
                detail="Invalid instructor"
            )

    # Validate topic if provided
    if payload.topic_id:

        topic = db.query(Topic).filter(
            Topic.topic_id == payload.topic_id
        ).first()

        if not topic:
            raise HTTPException(
                status_code=404,
                detail="Topic not found"
            )

    # Insert content
    return content_repo.create_content(
        db,
        payload.dict()
    )


# FETCH COURSE CONTENT

def get_course_content_service(db: Session, course_id: int):

    course = course_repo.get_course_by_id(db, course_id)

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    return content_repo.get_content_by_course(
        db,
        course_id
    )


# FETCH TOPIC CONTENT

def get_topic_content_service(db: Session, topic_id: int):

    return content_repo.get_content_by_topic(
        db,
        topic_id
    )