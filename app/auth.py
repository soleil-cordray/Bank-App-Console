# app/auth.py
# WAS docs/archive/auth.py (same idea, now reading logins from MongoDB)
# Who is calling, and are they allowed? Controllers add one of these with Depends(...):
#   user=Depends(get_current_user) -> any logged-in user (admin or customer)
#   user=Depends(customer_only)    -> customers only (admins get 403)
#   user=Depends(admin_only)       -> the admin only (customers get 403)
# BASIC LOGIN: plain username + password (HTTP Basic), no hashing or tokens yet.
# HTTPBasic also adds the "Authorize" button to /docs.

import os
import secrets
from dataclasses import dataclass

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.repositories.customer_repository import customer_repository

# ADMIN: one admin login, set in .env (defaults match the old Java app)
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

security = HTTPBasic()


@dataclass
class CurrentUser:
    '''The logged-in caller.'''
    username: str
    role: str # "ADMIN" or "CUSTOMER"
    customer_id: int | None = None # None for the admin

    @property
    def is_admin(self):
        return self.role == "ADMIN"

    def scope(self):
        # what a read is limited to: None = everything (admin), else only this customer's things
        return None if self.is_admin else self.customer_id


def _same(given, expected):
    # compare_digest takes the same time whether or not the text matches (no timing hints)
    return secrets.compare_digest(given.encode(), expected.encode())


def get_current_user(credentials: HTTPBasicCredentials = Depends(security)) -> CurrentUser:
    '''Checks username + password; 401 if wrong, 403 if the customer was deactivated.'''
    if _same(credentials.username, ADMIN_USERNAME) and _same(credentials.password, ADMIN_PASSWORD):
        return CurrentUser(username=ADMIN_USERNAME, role="ADMIN")

    customer = customer_repository.get_by_username(credentials.username)
    if customer is None or not _same(credentials.password, customer["password"]):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    # a deactivated customer's login stops working immediately
    if not customer["is_active"]:
        raise HTTPException(status_code=403, detail="This customer has been deactivated")
    return CurrentUser(username=customer["username"], role="CUSTOMER", customer_id=customer["customer_id"])


def customer_only(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    # admins can view, but never change a customer's data or move money
    if user.is_admin:
        raise HTTPException(status_code=403, detail="Admins cannot make changes or transactions for customers")
    return user


def admin_only(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Only an admin can do this")
    return user
