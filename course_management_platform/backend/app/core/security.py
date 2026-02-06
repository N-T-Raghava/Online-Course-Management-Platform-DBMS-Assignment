from passlib.context import CryptContext

# Password Hashing Context
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

# Hash Password
def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt.
    """
    return pwd_context.hash(password)

# Verify Password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Compare plain password with hashed password.
    """
    return pwd_context.verify(plain_password, hashed_password)