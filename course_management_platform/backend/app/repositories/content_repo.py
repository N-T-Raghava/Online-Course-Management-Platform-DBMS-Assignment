from sqlalchemy.orm import Session
from datetime import date

from app.models.course_content import CourseContent


# CREATE CONTENT
def create_content(db: Session, data: dict):

    content = CourseContent(
        **data,
        upload_date=date.today()
    )

    db.add(content)
    db.commit()
    db.refresh(content)

    return content


# FETCH CONTENT

def get_content_by_course(db: Session, course_id: int):
    return db.query(CourseContent).filter(
        CourseContent.course_id == course_id
    ).all()


def get_content_by_topic(db: Session, topic_id: int):
    return db.query(CourseContent).filter(
        CourseContent.topic_id == topic_id
    ).all()
    
# DELETE CONTENT
def delete_content(db: Session, content_id: int):
    content = db.query(CourseContent).filter(
        CourseContent.id == content_id
    ).first()

    if content:
        db.delete(content)
        db.commit()
        return True
    return False

