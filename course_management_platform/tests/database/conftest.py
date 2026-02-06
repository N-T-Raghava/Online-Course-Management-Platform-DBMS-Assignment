"""
Minimal pytest configuration: ensure `backend` is on path and env loaded.
"""
import sys
import os

from pathlib import Path
from dotenv import load_dotenv

# Ensure backend package is importable
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend"))
sys.path.insert(0, backend_path)

# Load environment variables from project .env if present
load_dotenv(Path(__file__).parent.parent.parent / '.env')
