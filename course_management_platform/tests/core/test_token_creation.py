import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.app.core.jwt_handler import create_access_token, decode_access_token

data = {
    "user_id": 1,
    "role": "Student"
}

token = create_access_token(data)

print("Token:", token)

decoded = decode_access_token(token)

print("Decoded:", decoded)