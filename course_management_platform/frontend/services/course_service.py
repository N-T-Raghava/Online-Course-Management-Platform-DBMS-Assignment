import requests
import os
from typing import Tuple, Any

BACKEND_URL = os.getenv('BACKEND_URL', 'http://127.0.0.1:8000')


class CourseService:
    """Frontend service to fetch course data from backend APIs"""

    @staticmethod
    def get_all_courses() -> Tuple[bool, Any]:
        try:
            resp = requests.get(f"{BACKEND_URL}/courses", timeout=10)
            if resp.status_code == 200:
                return True, resp.json()
            return False, resp.json() if resp.text else []
        except requests.exceptions.RequestException:
            return False, []

    @staticmethod
    def get_all_universities() -> Tuple[bool, Any]:
        """Fetch all universities"""
        try:
            resp = requests.get(f"{BACKEND_URL}/universities", timeout=10)
            if resp.status_code == 200:
                return True, resp.json()
            return False, []
        except requests.exceptions.RequestException:
            return False, []

    @staticmethod
    def get_course_by_id(course_id: int) -> Tuple[bool, Any]:
        try:
            resp = requests.get(f"{BACKEND_URL}/courses/{course_id}", timeout=10)
            if resp.status_code == 200:
                return True, resp.json()
            return False, None
        except requests.exceptions.RequestException:
            return False, None

    @staticmethod
    def get_course_content(course_id: int) -> Tuple[bool, Any]:
        try:
            resp = requests.get(f"{BACKEND_URL}/content/course/{course_id}", timeout=10)
            if resp.status_code == 200:
                return True, resp.json()
            return False, []
        except requests.exceptions.RequestException:
            return False, []

    @staticmethod
    def get_university_by_course(course_id: int) -> Tuple[bool, Any]:
        """Fetch the university information for a given course_id"""
        try:
            resp = requests.get(f"{BACKEND_URL}/courses/{course_id}/university", timeout=10)
            if resp.status_code == 200:
                return True, resp.json()
            return False, resp.json() if resp.text else None
        except requests.exceptions.RequestException:
            return False, None

    @staticmethod
    def get_topics_by_course(course_id: int) -> Tuple[bool, Any]:
        """Fetch all topics for a given course_id"""
        try:
            resp = requests.get(f"{BACKEND_URL}/courses/{course_id}/topics", timeout=10)
            if resp.status_code == 200:
                return True, resp.json()
            return False, []
        except requests.exceptions.RequestException:
            return False, []

    @staticmethod
    def get_public_reviews_by_course(course_id: int) -> Tuple[bool, Any]:
        """Fetch all public reviews for a given course_id"""
        try:
            resp = requests.get(f"{BACKEND_URL}/enrollments/reviews/{course_id}", timeout=10)
            if resp.status_code == 200:
                return True, resp.json()
            return False, []
        except requests.exceptions.RequestException:
            return False, []

    @staticmethod
    def create_instructor_course(course_data: dict, token: str) -> Tuple[bool, Any]:
        """Create a new course as an instructor (pending approval)"""
        try:
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            resp = requests.post(
                f"{BACKEND_URL}/courses/instructor/create",
                json=course_data,
                headers=headers,
                timeout=10
            )
            
            # Always try to parse response as JSON
            try:
                response_data = resp.json()
            except:
                response_data = {"error": resp.text or "Unknown error"}
            
            if resp.status_code in [200, 201]:
                return True, response_data
            
            # For error responses, return the full error details
            return False, response_data
        except requests.exceptions.RequestException as e:
            return False, {"error": str(e)}

    @staticmethod
    def get_instructor_pending_courses(token: str) -> Tuple[bool, Any]:
        """Get instructor's courses pending approval"""
        try:
            headers = {
                'Authorization': f'Bearer {token}',
            }
            resp = requests.get(
                f"{BACKEND_URL}/courses/instructor/pending",
                headers=headers,
                timeout=10
            )
            if resp.status_code == 200:
                return True, resp.json()
            return False, []
        except requests.exceptions.RequestException:
            return False, []
