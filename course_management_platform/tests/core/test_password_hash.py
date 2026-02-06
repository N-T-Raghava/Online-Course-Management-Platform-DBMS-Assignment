import sys
from pathlib import Path

# Ensure backend package is importable
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.app.core.security import hash_password, verify_password

pw = "test123"

hashed = hash_password(pw)

print("Hashed:", hashed)
print("Match:", verify_password(pw, hashed))
