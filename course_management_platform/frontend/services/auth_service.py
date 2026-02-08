import requests
import os
from typing import Dict, Any, Optional

BACKEND_URL = os.getenv('BACKEND_URL', 'http://127.0.0.1:8000')

class AuthService:
    """Service for handling authentication API calls"""
    
    @staticmethod
    def register(data: Dict[str, Any]) -> tuple[bool, Dict[str, Any]]:
        """
        Register a new user
        
        Args:
            data: User registration data
            
        Returns:
            Tuple of (success: bool, response: dict)
        """
        try:
            response = requests.post(
                f'{BACKEND_URL}/auth/register',
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, response.json() if response.text else {'error': 'Registration failed'}
        except requests.exceptions.RequestException as e:
            return False, {'error': f'Connection error: {str(e)}'}
    
    @staticmethod
    def login(email: str, password: str) -> tuple[bool, Dict[str, Any]]:
        """
        Login user
        
        Args:
            email: User email
            password: User password
            
        Returns:
            Tuple of (success: bool, response: dict)
        """
        try:
            response = requests.post(
                f'{BACKEND_URL}/auth/login',
                json={
                    'email': email,
                    'password': password
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, response.json() if response.text else {'error': 'Login failed'}
        except requests.exceptions.RequestException as e:
            return False, {'error': f'Connection error: {str(e)}'}
    
    @staticmethod
    def get_current_user(token: str) -> tuple[bool, Dict[str, Any]]:
        """
        Get current user info
        
        Args:
            token: Bearer token
            
        Returns:
            Tuple of (success: bool, response: dict)
        """
        try:
            response = requests.get(
                f'{BACKEND_URL}/auth/me',
                headers={'Authorization': f'Bearer {token}'},
                timeout=10
            )
            
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, response.json() if response.text else {'error': 'Failed to fetch user'}
        except requests.exceptions.RequestException as e:
            return False, {'error': f'Connection error: {str(e)}'}
