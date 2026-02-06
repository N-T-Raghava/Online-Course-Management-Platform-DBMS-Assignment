from sqlalchemy.orm import Session

from app.models.user import User
from app.models.student import Student
from app.models.instructor import Instructor
from app.models.administrator import Administrator
from app.models.data_analyst import DataAnalyst

# Create Base User
def create_user(db: Session, user_data: dict) -> User:
    user = User(**user_data)

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

# Get User By Email
def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()

# Get User By ID
def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.user_id == user_id).first()

# Create Student Subclass
def create_student(db: Session, user_id: int, data: dict):
    student = Student(user_id=user_id, **data)

    db.add(student)
    db.commit()

# Create Instructor Subclass
def create_instructor(db: Session, user_id: int, data: dict):
    instructor = Instructor(user_id=user_id, **data)

    db.add(instructor)
    db.commit()

# Create Administrator Subclass
def create_administrator(db: Session, user_id: int, data: dict):
    admin = Administrator(user_id=user_id, **data)

    db.add(admin)
    db.commit()

# Create Data Analyst Subclass
def create_data_analyst(db: Session, user_id: int, data: dict):
    analyst = DataAnalyst(user_id=user_id, **data)

    db.add(analyst)
    db.commit()