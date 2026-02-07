from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.content_schema import (
    ContentCreate,
    ContentResponse
)
from app.services.content_service import (
    upload_content_service,
    get_course_content_service,
    get_topic_content_service
)

# 🔐 JWT Dependency
from app.core.dependencies import get_current_user

# Router Config
router = APIRouter(
    prefix="/content",
    tags=["Content Management"]
)

# ------------------------------------------------------------
# Upload Content
# • Instructor → Only assigned courses
# • Admin → Override allowed
# ------------------------------------------------------------
@router.post(
    "/upload",
    response_model=ContentResponse
)
def upload_content(
    payload: ContentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return upload_content_service(
        db,
        payload,
        current_user
    )


# ------------------------------------------------------------
# Get Course Content → OPEN
# ------------------------------------------------------------
@router.get(
    "/course/{course_id}",
    response_model=list[ContentResponse]
)
def get_course_content(
    course_id: int,
    db: Session = Depends(get_db)
):
    return get_course_content_service(
        db,
        course_id
    )


# ------------------------------------------------------------
# Get Topic Content → OPEN
# ------------------------------------------------------------
@router.get(
    "/topic/{topic_id}",
    response_model=list[ContentResponse]
)
def get_topic_content(
    topic_id: int,
    db: Session = Depends(get_db)
):
    return get_topic_content_service(
        db,
        topic_id
    )