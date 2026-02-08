# Plain text password storage (no hashing)
# Password is stored directly as entered by user

def store_password(password: str) -> str:
    """
    Store password as plain text (no hashing).
    Returns the password as-is.
    """
    return password


def verify_password(plain_password: str, stored_password: str) -> bool:
    """
    Compare plain text passwords directly.
    """
    return plain_password == stored_password