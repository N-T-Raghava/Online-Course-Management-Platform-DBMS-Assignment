from sqlalchemy.orm import Session

from app.models.university import University
from app.models.course import Course
from app.models.topic import Topic
from app.models.course_topic import CourseTopic

# UNIVERSITY OPERATIONS
def create_university(db: Session, data: dict) -> University:
    university = University(**data)

    db.add(university)
    db.commit()
    db.refresh(university)

    return university


def get_all_universities(db: Session):
    return db.query(University).all()


def get_university_by_id(db: Session, university_id: int):
    return db.query(University).filter(
        University.university_id == university_id
    ).first()

# COURSE OPERATIONS
def create_course(db: Session, data: dict) -> Course:
    course = Course(**data)

    db.add(course)
    db.commit()
    db.refresh(course)

    return course


def get_all_courses(db: Session):
    return db.query(Course).all()


def get_course_by_id(db: Session, course_id: int):
    return db.query(Course).filter(
        Course.course_id == course_id
    ).first()


def get_university_by_course(db: Session, course_id: int):
    # Fetch the course and return its related university if present
    course = get_course_by_id(db, course_id)
    if not course:
        return None
    return course.university


# TOPIC OPERATIONS
def create_topic(db: Session, data: dict) -> Topic:
    topic = Topic(**data)

    db.add(topic)
    db.commit()
    db.refresh(topic)

    return topic


def get_all_topics(db: Session):
    return db.query(Topic).all()


def get_topic_by_id(db: Session, topic_id: int):
    return db.query(Topic).filter(
        Topic.topic_id == topic_id
    ).first()

# COURSE ↔ TOPIC MAPPING
def map_topic_to_course(
    db: Session,
    course_id: int,
    topic_id: int,
    sequence_order: int | None = None
):
    mapping = CourseTopic(
        course_id=course_id,
        topic_id=topic_id,
        sequence_order=sequence_order
    )

    db.add(mapping)
    db.commit()

    return mapping


def get_topics_by_course(db: Session, course_id: int):
    # Join CourseTopic with Topic to get full topic details, ordered by sequence_order
    return db.query(Topic).join(
        CourseTopic,
        CourseTopic.topic_id == Topic.topic_id
    ).filter(
        CourseTopic.course_id == course_id
    ).order_by(CourseTopic.sequence_order).all()