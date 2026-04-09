import hashlib
from passlib.context import CryptContext

# 🔐 bcrypt configuration
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12   # 🔥 cost factor (secure + performant)
)

# =========================================================
# ✅ PASSWORD VALIDATION
# =========================================================
def validate_password(password: str):
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")

    if not any(c.isupper() for c in password):
        raise ValueError("Password must contain at least one uppercase letter")

    if not any(c.islower() for c in password):
        raise ValueError("Password must contain at least one lowercase letter")

    if not any(c.isdigit() for c in password):
        raise ValueError("Password must contain at least one number")

    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        raise ValueError("Password must contain at least one special character")

    return True


# =========================================================
# ✅ HASH PASSWORD (PRODUCTION SAFE)
# =========================================================
def hash_password(password: str):
    # 🔍 Validate password
    validate_password(password)

    # 🔥 Pre-hash using SHA256 (removes bcrypt 72-byte limit)
    sha_password = hashlib.sha256(password.encode()).hexdigest()

    # 🔐 bcrypt hash
    return pwd_context.hash(sha_password)


# =========================================================
# ✅ VERIFY PASSWORD
# =========================================================
def verify_password(plain_password: str, hashed_password: str):
    sha_password = hashlib.sha256(plain_password.encode()).hexdigest()
    return pwd_context.verify(sha_password, hashed_password)