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
    return db.query(Course).filter(
        Course.approval_status == 'Approved'
    ).all()


def get_approved_courses(db: Session):
    """Get only approved courses"""
    return db.query(Course).filter(
        Course.approval_status == 'Approved'
    ).all()


def get_all_categories(db: Session):
    """Get all distinct approved course categories"""
    categories = db.query(Course.category).filter(
        Course.approval_status == 'Approved',
        Course.category.isnot(None),
        Course.category != ''
    ).distinct().order_by(Course.category).all()
    
    # Extract category names from query result tuples
    return [cat[0] for cat in categories if cat[0]]


def get_courses_by_category(db: Session, category: str):
    """Get all approved courses for a specific category"""
    return db.query(Course).filter(
        Course.approval_status == 'Approved',
        Course.category == category
    ).all()


def get_pending_courses_by_instructor(db: Session, instructor_user_id: int):
    """Get courses pending approval created by specific instructor"""
    return db.query(Course).filter(
        Course.created_by == instructor_user_id,
        Course.approval_status == 'Pending'
    ).all()


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


def get_topic_by_name(db: Session, topic_name: str):
    """Get a topic by its name"""
    return db.query(Topic).filter(
        Topic.name == topic_name
    ).first()


def update_topic_sequence(db: Session, course_id: int, topic_id: int, sequence_order: int):
    """Update the sequence order of a topic in a course"""
    mapping = db.query(CourseTopic).filter(
        CourseTopic.course_id == course_id,
        CourseTopic.topic_id == topic_id
    ).first()
    
    if mapping:
        mapping.sequence_order = sequence_order
        db.commit()
    
    return mapping

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


def delete_topic_mapping(db: Session, course_id: int, topic_id: int):
    """Delete a CourseTopic mapping and return True if removed"""
    mapping = db.query(CourseTopic).filter(
        CourseTopic.course_id == course_id,
        CourseTopic.topic_id == topic_id
    ).first()

    if not mapping:
        return False

    db.delete(mapping)
    db.commit()

    return True


def get_course_topic_mappings(db: Session, course_id: int):
    """Return CourseTopic mappings ordered by sequence_order"""
    return db.query(CourseTopic).filter(
        CourseTopic.course_id == course_id
    ).order_by(CourseTopic.sequence_order).all()