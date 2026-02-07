# backend/app/core/roles.py
from enum import Enum

# SYSTEM ROLES
class Role(str, Enum):
    STUDENT = "Student"
    INSTRUCTOR = "Instructor"
    ADMIN = "Administrator"
    ANALYST = "Data Analyst"

# ADMIN LEVELS
class AdminLevel(str, Enum):
    JUNIOR = "Junior"
    SENIOR = "Senior"