import requests
import os
from typing import Dict, Any, Optional

BACKEND_URL = os.getenv('BACKEND_URL', 'http://127.0.0.1:8000')

class AdminService:
    """Service for handling admin-related API calls"""
    
    @staticmethod
    def get_current_admin(token: str) -> tuple[bool, Dict[str, Any]]:
        """Get current admin user info"""
        try:
            response = requests.get(
                f'{BACKEND_URL}/auth/me',
                headers={'Authorization': f'Bearer {token}'},
                timeout=10
            )
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, response.json() if response.text else {'error': 'Failed to fetch admin info'}
        except requests.exceptions.RequestException as e:
            return False, {'error': f'Connection error: {str(e)}'}
    
    @staticmethod
    def get_all_courses(token: str) -> tuple[bool, list]:
        """Fetch all courses"""
        try:
            response = requests.get(
                f'{BACKEND_URL}/courses',
                headers={'Authorization': f'Bearer {token}'},
                timeout=10
            )
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, []
        except requests.exceptions.RequestException as e:
            return False, []
    
    @staticmethod
    def get_course_analytics(course_id: int, token: str) -> tuple[bool, Dict[str, Any]]:
        """Fetch analytics for a specific course"""
        try:
            response = requests.get(
                f'{BACKEND_URL}/analytics/courses/{course_id}',
                headers={'Authorization': f'Bearer {token}'},
                timeout=10
            )
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, {}
        except requests.exceptions.RequestException as e:
            return False, {}
    
    @staticmethod
    def get_all_instructors(token: str) -> tuple[bool, list]:
        """Fetch all instructors - via users endpoint filtering"""
        try:
            response = requests.get(
                f'{BACKEND_URL}/users/instructors',
                headers={'Authorization': f'Bearer {token}'},
                timeout=10
            )
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, []
        except requests.exceptions.RequestException as e:
            return False, []
    
    @staticmethod
    def get_instructors_by_course(course_id: int, token: str) -> tuple[bool, list]:
        """Fetch instructors for a specific course"""
        try:
            response = requests.get(
                f'{BACKEND_URL}/teaching/course/{course_id}',
                headers={'Authorization': f'Bearer {token}'},
                timeout=10
            )
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, []
        except requests.exceptions.RequestException as e:
            return False, []
    
    @staticmethod
    def assign_instructor(payload: Dict[str, Any], token: str) -> tuple[bool, Dict[str, Any]]:
        """Assign instructor to course"""
        try:
            response = requests.post(
                f'{BACKEND_URL}/teaching/assign',
                json=payload,
                headers={'Authorization': f'Bearer {token}'},
                timeout=10
            )
            if response.status_code in [200, 201]:
                return True, response.json()
            else:
                return False, response.json() if response.text else {'error': 'Failed to assign instructor'}
        except requests.exceptions.RequestException as e:
            return False, {'error': f'Connection error: {str(e)}'}
    
    @staticmethod
    def remove_instructor(course_id: int, instructor_user_id: int, token: str) -> tuple[bool, Dict[str, Any]]:
        """Remove instructor from course"""
        try:
            response = requests.delete(
                f'{BACKEND_URL}/admin/teaching/{course_id}/{instructor_user_id}',
                headers={'Authorization': f'Bearer {token}'},
                timeout=10
            )
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, response.json() if response.text else {'error': 'Failed to remove instructor'}
        except requests.exceptions.RequestException as e:
            return False, {'error': f'Connection error: {str(e)}'}
    
    @staticmethod
    def get_all_users(token: str) -> tuple[bool, list]:
        """Fetch all users (Senior Admin only)"""
        try:
            response = requests.get(
                f'{BACKEND_URL}/users',
                headers={'Authorization': f'Bearer {token}'},
                timeout=10
            )
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, []
        except requests.exceptions.RequestException as e:
            return False, []
    
    @staticmethod
    def delete_user(user_id: int, token: str) -> tuple[bool, Dict[str, Any]]:
        """Delete a user (Senior Admin only)"""
        try:
            response = requests.delete(
                f'{BACKEND_URL}/admin/users/{user_id}',
                headers={'Authorization': f'Bearer {token}'},
                timeout=10
            )
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, response.json() if response.text else {'error': 'Failed to delete user'}
        except requests.exceptions.RequestException as e:
            return False, {'error': f'Connection error: {str(e)}'}
    
    @staticmethod
    def delete_review(student_user_id: int, course_id: int, token: str) -> tuple[bool, Dict[str, Any]]:
        """Delete a course review (Moderation)"""
        try:
            response = requests.delete(
                f'{BACKEND_URL}/moderation/review/{student_user_id}/{course_id}',
                headers={'Authorization': f'Bearer {token}'},
                timeout=10
            )
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, response.json() if response.text else {'error': 'Failed to delete review'}
        except requests.exceptions.RequestException as e:
            return False, {'error': f'Connection error: {str(e)}'}
    
    @staticmethod
    def override_rating(student_user_id: int, course_id: int, rating: int, token: str) -> tuple[bool, Dict[str, Any]]:
        """Override student rating (Moderation)"""
        try:
            response = requests.put(
                f'{BACKEND_URL}/moderation/rating/{student_user_id}/{course_id}/{rating}',
                headers={'Authorization': f'Bearer {token}'},
                timeout=10
            )
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, response.json() if response.text else {'error': 'Failed to override rating'}
        except requests.exceptions.RequestException as e:
            return False, {'error': f'Connection error: {str(e)}'}
    
    @staticmethod
    def force_completion(student_user_id: int, course_id: int, token: str) -> tuple[bool, Dict[str, Any]]:
        """Force mark course as complete (Moderation)"""
        try:
            response = requests.put(
                f'{BACKEND_URL}/moderation/completion/{student_user_id}/{course_id}',
                headers={'Authorization': f'Bearer {token}'},
                timeout=10
            )
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, response.json() if response.text else {'error': 'Failed to force completion'}
        except requests.exceptions.RequestException as e:
            return False, {'error': f'Connection error: {str(e)}'}
    
    @staticmethod
    def get_platform_analytics(token: str) -> tuple[bool, Dict[str, Any]]:
        """Get overall platform analytics"""
        try:
            response = requests.get(
                f'{BACKEND_URL}/analytics/platform',
                headers={'Authorization': f'Bearer {token}'},
                timeout=10
            )
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, {}
        except requests.exceptions.RequestException as e:
            return False, {}
