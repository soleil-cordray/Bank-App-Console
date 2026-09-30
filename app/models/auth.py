# app/models/auth.py
# NEW. Request / response shapes for logins.
# REFS: 5A.1 (registration + login), 5A.3 (the four roles)

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.models.customer import EMAIL_PATTERN

# ROLES [5A.3]
Role = Literal["CUSTOMER", "TELLER", "BRANCH_MANAGER", "ADMIN"]


def _lowercase(value):
    # "Rohit@X.com" and "rohit@x.com" are the same login
    return value.strip().lower() if isinstance(value, str) else value


class RegisterRequest(BaseModel):
    '''Body of POST /api/v1/auth/register (a customer creates their login).'''
    # the email must match an existing customer profile
    email: str = Field(..., pattern=EMAIL_PATTERN)
    # bcrypt only reads the first 72 bytes, so longer passwords are refused
    password: str = Field(..., min_length=8, max_length=72)

    _normalize_email = field_validator("email", mode="before")(_lowercase)


class Login(BaseModel):
    '''What the API returns for a login. Never includes password_hash.'''
    login_id: int
    email: str
    role: Role
    customer_id: int | None = None
    branch_id: int | None = None
    created_at: datetime
    is_active: bool


class Token(BaseModel):
    '''What POST /api/v1/auth/login returns. [5A.2]'''
    access_token: str
    token_type: str = "bearer"


class CurrentUser(BaseModel):
    '''Who is making the request, read from their token. [5A.2]'''
    login_id: int
    email: str
    role: Role
    customer_id: int | None = None
    branch_id: int | None = None
