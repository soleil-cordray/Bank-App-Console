# app/security.py
# NEW. Password hashing (bcrypt) and JWT tokens (PyJWT).
# Plain helper functions: no FastAPI here, so services can use them.
# REFS: 5A.1 (bcrypt salted hashing), 5A.2 (JWT with sub, email, roles)

import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from dotenv import load_dotenv

# READ: secret settings from .env (never hardcoded, never pushed)
load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "30"))

if not JWT_SECRET:
    # fail fast: without a secret, anyone could forge tokens
    raise RuntimeError("JWT_SECRET is missing from .env")


# PASSWORDS [5A.1] ------------------------------------------------------------

def hash_password(password: str) -> str:
    # bcrypt adds a random salt, so the same password hashes differently each time
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    # bcrypt reads the salt back out of the hash and compares
    return bcrypt.checkpw(password.encode(), password_hash.encode())


# TOKENS [5A.2] ---------------------------------------------------------------

def create_access_token(login: dict) -> str:
    '''Build a signed JWT for a saved login document.'''
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(login["login_id"]),  # who the token belongs to ("subject")
        "email": login["email"],
        "roles": [login["role"]],       # a list, as the chapter asks
        "customer_id": login.get("customer_id"),  # set for CUSTOMER logins
        "branch_id": login.get("branch_id"),      # set for TELLER / BRANCH_MANAGER
        "iat": now,                                # issued at
        "exp": now + timedelta(minutes=JWT_EXPIRE_MINUTES),  # expires at
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    '''Check the signature and expiry. Raises jwt.PyJWTError if either is bad.'''
    return jwt.decode(
        token, JWT_SECRET, algorithms=[JWT_ALGORITHM],
        options={"require": ["sub", "exp"]},
    )
