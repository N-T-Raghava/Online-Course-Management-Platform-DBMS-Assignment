from passlib.context import CryptContext

# ---------------------------------------------------
# Password Hashing Config
# ---------------------------------------------------

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

# ---------------------------------------------------
# Hash Password
# ---------------------------------------------------

def store_password(password: str) -> str:
    """
    Hash a plain password using bcrypt.
    """
    return pwd_context.hash(password)


# ---------------------------------------------------
# Verify Password
# ---------------------------------------------------

def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    """
    Verify plain password against hash.
    """
    return pwd_context.verify(
        plain_password,
        hashed_password
    )