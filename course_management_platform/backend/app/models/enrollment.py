from sqlalchemy import Column, Integer, Date, String, Text, TIMESTAMP, ForeignKey, Boolean
from app.database import Base


class Enrollment(Base):
    __tablename__ = "enrollment"

    student_user_id = Column(Integer, ForeignKey("student.user_id", ondelete="CASCADE"), primary_key=True)
    course_id = Column(Integer, ForeignKey("course.course_id", ondelete="CASCADE"), primary_key=True)

    enrollment_date = Column(Date)
    status = Column(String(30))
    completion_status = Column(String(30))
    completion_date = Column(Date)

    rating = Column(Integer)
    review_text = Column(Text)
    is_review_public = Column(Boolean, default=False)  # New: track if review is public
    rated_at = Column(TIMESTAMP)

    grade = Column(String(5))