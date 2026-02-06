import sys
from pathlib import Path

# Ensure backend package is importable
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

import pytest
from sqlalchemy import text

from app.database import SessionLocal
from app.models import (
    User,
    Student,
    Instructor,
    Administrator,
    DataAnalyst,
    University,
    Course,
    Topic,
    CourseTopic,
    Enrollment,
    Teaching,
    CourseContent,
    Statistics,
    StudentStatistics,
    InstructorStatistics
)


# --------------------------------------------------
# Fixture → DB Session
# --------------------------------------------------

@pytest.fixture(scope="module")
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


# --------------------------------------------------
# 1️⃣ Connection Test
# --------------------------------------------------

def test_database_connection(db):
    result = db.execute(text("SELECT 1"))
    assert result.scalar() == 1


# --------------------------------------------------
# 2️⃣ User & ISA Tables
# --------------------------------------------------

def test_user_tables_accessible(db):
    db.query(User).limit(1).all()
    db.query(Student).limit(1).all()
    db.query(Instructor).limit(1).all()
    db.query(Administrator).limit(1).all()
    db.query(DataAnalyst).limit(1).all()


# --------------------------------------------------
# 3️⃣ Academic Core
# --------------------------------------------------

def test_academic_tables_accessible(db):
    db.query(University).limit(1).all()
    db.query(Course).limit(1).all()


# --------------------------------------------------
# 4️⃣ Topic System
# --------------------------------------------------

def test_topic_tables_accessible(db):
    db.query(Topic).limit(1).all()
    db.query(CourseTopic).limit(1).all()


# --------------------------------------------------
# 5️⃣ Participation
# --------------------------------------------------

def test_participation_tables_accessible(db):
    db.query(Enrollment).limit(1).all()
    db.query(Teaching).limit(1).all()


# --------------------------------------------------
# 6️⃣ Content System
# --------------------------------------------------

def test_content_tables_accessible(db):
    db.query(CourseContent).limit(1).all()


# --------------------------------------------------
# 7️⃣ Statistics Tables
# --------------------------------------------------

def test_statistics_tables_accessible(db):
    db.query(Statistics).limit(1).all()
    db.query(StudentStatistics).limit(1).all()
    db.query(InstructorStatistics).limit(1).all()
