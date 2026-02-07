from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.repositories import content_repo
from app.repositories import course_repo
from app.repositories import user_repo
from app.models.topic import Topic

from app.repositories.participation_repo import get_teaching_assignment
from app.core.roles import Role

# UPLOAD CONTENT
def upload_content_service(
    db: Session,
    payload,
    current_user: dict
):

    # --------------------------------------------------------
    # COURSE VALIDATION
    # --------------------------------------------------------

    course = course_repo.get_course_by_id(
        db,
        payload.course_id
    )

    if not course:
        raise HTTPException(404, "Course not found")

    # --------------------------------------------------------
    # INSTRUCTOR OWNERSHIP CHECK
    # --------------------------------------------------------

    if current_user["role"] == Role.INSTRUCTOR.value:

        teaching = get_teaching_assignment(
            db,
            current_user["user_id"],
            payload.course_id
        )

        if not teaching:
            raise HTTPException(
                status_code=403,
                detail="Instructor not assigned to this course"
            )

        payload.instructor_user_id = current_user["user_id"]

    # --------------------------------------------------------
    # ADMIN OVERRIDE
    # --------------------------------------------------------

    if payload.instructor_user_id:

        user = user_repo.get_user_by_id(
            db,
            payload.instructor_user_id
        )

        if not user or user.role.lower() != "instructor":
            raise HTTPException(400, "Invalid instructor")

    # Topic validation
    if payload.topic_id:

        topic = db.query(Topic).filter(
            Topic.topic_id == payload.topic_id
        ).first()

        if not topic:
            raise HTTPException(404, "Topic not found")

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