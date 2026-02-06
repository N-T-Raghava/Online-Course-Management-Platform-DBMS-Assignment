import os

backend_app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "app"))
if os.path.isdir(backend_app_path):
	__path__.insert(0, backend_app_path)

from backend.app import *
