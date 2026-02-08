import requests
import os
from typing import Dict, Any, Optional, Tuple

BACKEND_URL = os.getenv('BACKEND_URL', 'http://127.0.0.1:8000')


class InstructorService:
    """Service for handling instructor-related API calls"""
    
    @staticmethod
    def get_current_instructor(token: str) -> Tuple[bool, Any]:
        """Fetch current instructor info from JWT token"""
        try:
            resp = requests.get(
                f"{BACKEND_URL}/auth/me",
                headers={'Authorization': f'Bearer {token}'},
                timeout=10
            )
            if resp.status_code == 200:
                return True, resp.json()
            return False, None
        except requests.exceptions.RequestException as e:
            return False, {'error': str(e)}
    
    @staticmethod
    def get_instructor_analytics(user_id: int, token: str) -> Tuple[bool, Any]:
        """Fetch analytics for an instructor"""
        try:
            resp = requests.get(
                f"{BACKEND_URL}/analytics/instructors/{user_id}",
                headers={'Authorization': f'Bearer {token}'},
                timeout=10
            )
            if resp.status_code == 200:
                return True, resp.json()
            return False, None
        except requests.exceptions.RequestException as e:
            return False, {'error': str(e)}
    
    @staticmethod
    def get_instructor_courses(user_id: int, token: str) -> Tuple[bool, Any]:
        """Fetch all courses taught by an instructor"""
        try:
            resp = requests.get(
                f"{BACKEND_URL}/teaching/instructor/{user_id}",
                headers={'Authorization': f'Bearer {token}'},
                timeout=10
            )
            if resp.status_code == 200:
                return True, resp.json()
            return False, []
        except requests.exceptions.RequestException as e:
            return False, {'error': str(e)}
    
    @staticmethod
    def get_course_details(course_id: int, token: str) -> Tuple[bool, Any]:
        """Fetch detailed course information"""
        try:
            resp = requests.get(
                f"{BACKEND_URL}/courses/{course_id}",
                headers={'Authorization': f'Bearer {token}'},
                timeout=10
            )
            if resp.status_code == 200:
                return True, resp.json()
            return False, None
        except requests.exceptions.RequestException as e:
            return False, {'error': str(e)}
    
    @staticmethod
    def get_course_analytics(course_id: int, token: str) -> Tuple[bool, Any]:
        """Fetch analytics for a specific course"""
        try:
            resp = requests.get(
                f"{BACKEND_URL}/analytics/courses/{course_id}",
                headers={'Authorization': f'Bearer {token}'},
                timeout=10
            )
            if resp.status_code == 200:
                return True, resp.json()
            return False, None
        except requests.exceptions.RequestException as e:
            return False, {'error': str(e)}
    
    @staticmethod
    def get_course_content(course_id: int, token: str) -> Tuple[bool, Any]:
        """Fetch all content for a course"""
        try:
            resp = requests.get(
                f"{BACKEND_URL}/content/course/{course_id}",
                headers={'Authorization': f'Bearer {token}'},
                timeout=10
            )
            if resp.status_code == 200:
                return True, resp.json()
            return False, []
        except requests.exceptions.RequestException as e:
            return False, []
    
    @staticmethod
    def get_course_topics(course_id: int, token: str) -> Tuple[bool, Any]:
        """Fetch topics for a course"""
        try:
            resp = requests.get(
                f"{BACKEND_URL}/topics/courses/{course_id}/topics",
                headers={'Authorization': f'Bearer {token}'},
                timeout=10
            )
            if resp.status_code == 200:
                return True, resp.json()
            return False, []
        except requests.exceptions.RequestException as e:
            return False, []
    
    @staticmethod
    def get_course_reviews(course_id: int, token: str) -> Tuple[bool, Any]:
        """Fetch reviews for a course"""
        try:
            resp = requests.get(
                f"{BACKEND_URL}/enrollments/reviews/{course_id}",
                headers={'Authorization': f'Bearer {token}'},
                timeout=10
            )
            if resp.status_code == 200:
                return True, resp.json()
            return False, []
        except requests.exceptions.RequestException as e:
            return False, []
    
    @staticmethod
    def upload_content(payload: Dict[str, Any], token: str) -> Tuple[bool, Any]:
        """Upload content to a course"""
        try:
            resp = requests.post(
                f"{BACKEND_URL}/content/upload",
                json=payload,
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
    def get_course_enrollments(course_id: int, token: str) -> Tuple[bool, Any]:
        """Fetch enrollment data for a course"""
        try:
            # This would typically come from analytics
            resp = requests.get(
                f"{BACKEND_URL}/analytics/courses/{course_id}",
                headers={'Authorization': f'Bearer {token}'},
                timeout=10
            )
            if resp.status_code == 200:
                return True, resp.json()
            return False, None
        except requests.exceptions.RequestException as e:
            return False, None
    
    @staticmethod
    def recompute_instructor_stats(user_id: int, token: str) -> Tuple[bool, Any]:
        """Recompute instructor statistics"""
        try:
            resp = requests.post(
                f"{BACKEND_URL}/analytics/recompute/instructor/{user_id}",
                headers={'Authorization': f'Bearer {token}'},
                timeout=10
            )
            if resp.status_code == 200:
                return True, resp.json()
            return False, None
        except requests.exceptions.RequestException as e:
            return False, None
