"""
Progress Service - Handles topic progression, assessment, and course completion
"""

import requests
import os
from typing import Tuple, Any
from datetime import datetime

BACKEND_URL = os.getenv('BACKEND_URL', 'http://127.0.0.1:8000')


class ProgressService:
    """Frontend service to manage student progress and assessments"""

    @staticmethod
    def get_course_topics(course_id: int, token: str = None) -> Tuple[bool, Any]:
        """
        Fetch all topics for a course, ordered by sequence_order.
        Returns: (success: bool, topics: list or error message)
        """
        try:
            headers = {}
            if token:
                headers['Authorization'] = f'Bearer {token}'
            
            resp = requests.get(
                f"{BACKEND_URL}/courses/{course_id}/topics",
                headers=headers,
                timeout=10
            )
            if resp.status_code == 200:
                return True, resp.json()
            return False, resp.json() if resp.text else []
        except requests.exceptions.RequestException as e:
            return False, []

    @staticmethod
    def get_enrollment(student_user_id: int, course_id: int, token: str = None) -> Tuple[bool, Any]:
        """
        Fetch enrollment data for a student in a course.
        Includes: enrollment_date, status, completion_status, grade, current_topic, etc.
        Returns: (success: bool, enrollment_data: dict or None)
        """
        try:
            headers = {}
            if token:
                headers['Authorization'] = f'Bearer {token}'
            
            resp = requests.get(
                f"{BACKEND_URL}/enrollments/student/{student_user_id}",
                headers=headers,
                timeout=10
            )
            if resp.status_code == 200:
                enrollments = resp.json()
                # Filter for specific course
                for enrollment in enrollments:
                    if enrollment.get('course_id') == course_id:
                        return True, enrollment
                return False, None
            return False, None
        except requests.exceptions.RequestException as e:
            return False, None

    @staticmethod
    def get_current_topic(student_user_id: int, course_id: int, token: str = None) -> Tuple[bool, Any]:
        """
        Fetch the current topic ID for a student in a course.
        Returns: (success: bool, current_topic_id: int or None)
        """
        success, enrollment = ProgressService.get_enrollment(student_user_id, course_id, token)
        if success and enrollment:
            current_topic = enrollment.get('current_topic')
            return True, current_topic
        return False, None

    @staticmethod
    def update_progress(
        student_user_id: int,
        course_id: int,
        topic_id: int,
        token: str = None
    ) -> Tuple[bool, Any]:
        """
        Update topic progression for a student.
        Updates: enrollment.current_topic = topic_id
        Returns: (success: bool, updated_enrollment: dict or error message)
        """
        try:
            headers = {}
            if token:
                headers['Authorization'] = f'Bearer {token}'
            
            resp = requests.put(
                f"{BACKEND_URL}/enrollments/progress/{student_user_id}/{course_id}/{topic_id}",
                headers=headers,
                timeout=10
            )
            if resp.status_code == 200:
                result = resp.json()
                return True, result
            error_msg = resp.json() if resp.text else "Failed to update progress"
            return False, error_msg
        except requests.exceptions.RequestException as e:
            return False, str(e)

    @staticmethod
    def submit_assessment(
        student_user_id: int,
        course_id: int,
        score: int = None,
        answers: list = None,
        token: str = None
    ) -> Tuple[bool, Any]:
        """
        Submit assessment with either precomputed score or answers array.
        Accepts either:
        - score: int (0-100 percentage)
        - answers: list of str (e.g., ['A', 'B', 'C', ...])
        
        Backend will compute score from answers if provided, or use precomputed score.
        Returns: (success: bool, result: dict with score, grade, completion_status)
        """
        try:
            headers = {}
            if token:
                headers['Authorization'] = f'Bearer {token}'
            
            payload = {}
            if score is not None:
                payload["score"] = score
            if answers is not None:
                payload["answers"] = answers
            
            if not payload:
                return False, "Either score or answers must be provided"
            
            resp = requests.post(
                f"{BACKEND_URL}/enrollments/assessment/{student_user_id}/{course_id}",
                json=payload,
                headers=headers,
                timeout=10
            )
            if resp.status_code == 200:
                return True, resp.json()
            return False, resp.json() if resp.text else "Failed to submit assessment"
        except requests.exceptions.RequestException as e:
            return False, str(e)

    @staticmethod
    def complete_course(
        student_user_id: int,
        course_id: int,
        token: str = None
    ) -> Tuple[bool, Any]:
        """
        Mark course as completed.
        Used after passing assessment (grade != F).
        Returns: (success: bool, updated_enrollment: dict or error message)
        """
        try:
            headers = {}
            if token:
                headers['Authorization'] = f'Bearer {token}'
            
            payload = {
                "completion_status": "Completed",
                "completion_date": str(datetime.today().date())
            }
            
            resp = requests.put(
                f"{BACKEND_URL}/enrollments/complete/{student_user_id}/{course_id}",
                json=payload,
                headers=headers,
                timeout=10
            )
            if resp.status_code == 200:
                return True, resp.json()
            return False, resp.json() if resp.text else "Failed to complete course"
        except requests.exceptions.RequestException as e:
            return False, str(e)

    @staticmethod
    def rate_course(
        student_user_id: int,
        course_id: int,
        rating: int,
        review_text: str = '',
        is_public: bool = False,
        token: str = None
    ) -> Tuple[bool, Any]:
        """
        Submit a course rating/review.
        Payload: {"rating": int, "review_text": str}
        Returns: (success: bool, result: dict or error message)
        """
        try:
            headers = {}
            if token:
                headers['Authorization'] = f'Bearer {token}'

            payload = {"rating": rating, "review_text": review_text, "is_public": bool(is_public)}

            resp = requests.post(
                f"{BACKEND_URL}/enrollments/rate/{student_user_id}/{course_id}",
                json=payload,
                headers=headers,
                timeout=10
            )
            if resp.status_code == 200:
                return True, resp.json()
            return False, resp.json() if resp.text else "Failed to submit rating"
        except requests.exceptions.RequestException as e:
            return False, str(e)


# Utility function for grade mapping (can be used on frontend)
def map_score_to_grade(score: int) -> str:
    """
    Map score (0-100 percentage) to grade.
    For 15-question quiz (converted to percentage):
    13–15 (86.67–100%) → A
    10–12 (66.67–86.66%) → B
    7–9 (46.67–66.66%) → C
    4–6 (26.67–46.66%) → D
    0–3 (0–26.66%) → F
    """
    if score >= 87:  # 13/15 = 86.67%
        return "A"
    elif score >= 67:  # 10/15 = 66.67%
        return "B"
    elif score >= 47:  # 7/15 = 46.67%
        return "C"
    elif score >= 27:  # 4/15 = 26.67%
        return "D"
    else:
        return "F"
