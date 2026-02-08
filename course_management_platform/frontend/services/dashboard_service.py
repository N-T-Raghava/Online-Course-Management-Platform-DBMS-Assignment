import requests
import os
from typing import Tuple, Any

BACKEND_URL = os.getenv('BACKEND_URL', 'http://127.0.0.1:8000')


class DashboardService:
    """Frontend service for dashboard operations"""

    @staticmethod
    def get_current_user(token: str) -> Tuple[bool, Any]:
        """Fetch current user info from JWT token"""
        try:
            resp = requests.get(
                f"{BACKEND_URL}/auth/me",
                headers={'Authorization': f'Bearer {token}'},
                timeout=10
            )
            if resp.status_code == 200:
                return True, resp.json()
            return False, None
        except requests.exceptions.RequestException:
            return False, None

    @staticmethod
    def get_student_analytics(user_id: int, token: str) -> Tuple[bool, Any]:
        """Fetch analytics for a student"""
        try:
            resp = requests.get(
                f"{BACKEND_URL}/analytics/students/{user_id}",
                headers={'Authorization': f'Bearer {token}'},
                timeout=10
            )
            if resp.status_code == 200:
                return True, resp.json()
            return False, None
        except requests.exceptions.RequestException:
            return False, None

    @staticmethod
    def get_all_courses() -> Tuple[bool, Any]:
        """Fetch all available courses"""
        try:
            resp = requests.get(f"{BACKEND_URL}/courses", timeout=10)
            if resp.status_code == 200:
                return True, resp.json()
            return False, []
        except requests.exceptions.RequestException:
            return False, []

    @staticmethod
    def enroll_course(user_id: int, course_id: int, token: str) -> Tuple[bool, Any]:
        """Enroll student in a course"""
        try:
            resp = requests.post(
                f"{BACKEND_URL}/enrollments/",
                json={
                    'student_user_id': user_id,
                    'course_id': course_id
                },
                headers={'Authorization': f'Bearer {token}'},
                timeout=10
            )
            if resp.status_code == 200:
                return True, resp.json()
            else:
                data = resp.json() if resp.text else {}
                return False, data
        except requests.exceptions.RequestException as e:
            return False, {'error': str(e)}

    @staticmethod
    def get_student_enrollments(user_id: int, token: str) -> Tuple[bool, Any]:
        """Fetch all enrollments for a student with course details"""
        try:
            resp = requests.get(
                f"{BACKEND_URL}/enrollments/student/{user_id}",
                headers={'Authorization': f'Bearer {token}'},
                timeout=10
            )
            if resp.status_code == 200:
                return True, resp.json()
            return False, []
        except requests.exceptions.RequestException:
            return False, []

    @staticmethod
    def recompute_student_stats(user_id: int, token: str) -> Tuple[bool, Any]:
        """Recompute student statistics (total enrollments, completed courses, etc.)"""
        try:
            resp = requests.post(
                f"{BACKEND_URL}/analytics/recompute/student/{user_id}",
                headers={'Authorization': f'Bearer {token}'},
                timeout=10
            )
            if resp.status_code == 200:
                return True, resp.json()
            return False, None
        except requests.exceptions.RequestException:
            return False, None
